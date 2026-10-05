import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

BRIDGE = Path(__file__).resolve().parents[1] / 'bin/mint-bridge'
loader = importlib.machinery.SourceFileLoader('bridge', str(BRIDGE))
spec = importlib.util.spec_from_loader(loader.name, loader)
bridge = importlib.util.module_from_spec(spec)
loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def test_generation_options_no_shell(self):
        with patch.object(bridge, 'run', return_value=b'{"password":"invented"}') as run:
            result = bridge.dispatch({'operation': 'generate', 'length': '10-16',
                                      'classes': ['lower', 'digits'], 'symbols': '!$()', 'noAmbiguous': True})
        self.assertEqual(result['password'], 'invented')
        self.assertEqual(run.call_args.args[0][1:], ['--json', '10-16', '--no-upper', '--no-symbols', '--no-ambiguous'])

    def test_save_new_password_no_existing_secret(self):
        with patch.object(bridge, 'run', return_value=b'{"password":"new"}') as run, patch.object(bridge, 'copy_password', return_value={'copied': True}):
            bridge.dispatch({'operation': 'save', 'title': '--item=other', 'vault': 'Test', 'length': 24})
        args = run.call_args.args[0]
        self.assertIn('--title=--item=other', args)
        self.assertEqual(args[1:3], ['save', '--show'])
        self.assertNotIn('--copy', args)
        with self.assertRaises(bridge.Failure):
            bridge.dispatch({'operation': 'save', 'title': 'Test', 'password': 'existing'})

    def test_save_sensitive_copy_failure_preserves_saved_result(self):
        responses = [b'{"password":"new-invented","id":"fake-id"}', bridge.Failure('failed'), b'other']
        with patch.object(bridge, 'run', side_effect=responses) as run:
            result = bridge.dispatch({'operation': 'save', 'title': 'Example', 'clearAfter': 0})
        self.assertEqual(result, {'password': 'new-invented', 'id': 'fake-id', 'copied': False})
        self.assertNotIn('--copy', run.call_args_list[0].args[0])
        self.assertEqual(run.call_args_list[0].kwargs['timeout'], 120)
        self.assertEqual(run.call_args_list[1].args, (['/usr/bin/wl-copy', '--sensitive'], b'new-invented'))
        self.assertEqual(run.call_args_list[2].args[0], ['/usr/bin/wl-paste', '--no-newline'])

    def test_save_invalid_delay_never_creates_item(self):
        with patch.object(bridge, 'run') as run:
            with self.assertRaises(bridge.Failure):
                bridge.dispatch({'operation': 'save', 'title': 'Example', 'clearAfter': -1})
        run.assert_not_called()

    def test_rejects_bad_inputs(self):
        for request in ({'operation': 'generate', 'length': '-5'},
                        {'operation': 'generate', 'classes': [['x']]},
                        {'operation': 'generate', 'length': 9999},
                        {'operation': 'copy', 'password': 'fake', 'clearAfter': -1},
                        {'operation': 'save', 'title': ''},
                        {'operation': 'exec', 'args': []}):
            with self.subTest(request=request), self.assertRaises(bridge.Failure):
                bridge.dispatch(request)

    def test_copy_secret_only_stdin_and_sensitive(self):
        with patch.object(bridge, 'run', return_value=b'') as run, patch.object(bridge.subprocess, 'Popen') as spawn, patch.object(bridge, 'handoff') as handoff:
            bridge.dispatch({'operation': 'copy', 'password': 'invented-secret'})
        self.assertEqual(run.call_args.args, (['/usr/bin/wl-copy', '--sensitive'], b'invented-secret'))
        self.assertFalse(run.call_args.kwargs['capture'])
        self.assertNotIn('invented-secret', repr(spawn.call_args))
        self.assertIn('-I', spawn.call_args.args[0])
        self.assertIn('-S', spawn.call_args.args[0])
        handoff.assert_called_once_with(spawn.return_value, b'invented-secret')

    def test_zero_delay_does_not_start_clearer(self):
        with patch.object(bridge, 'run', return_value=b'') as run, patch.object(bridge.subprocess, 'Popen') as spawn:
            result = bridge.dispatch({'operation': 'copy', 'password': 'invented', 'clearAfter': 0})
        self.assertEqual(result, {'copied': True, 'clears_after': None})
        self.assertEqual(run.call_args.args, (['/usr/bin/wl-copy', '--sensitive'], b'invented'))
        spawn.assert_not_called()

    def test_sensitive_failure_has_no_unhinted_fallback(self):
        with patch.object(bridge, 'run', side_effect=[bridge.Failure('failed'), b'other']) as run:
            with self.assertRaises(bridge.Failure) as error:
                bridge.dispatch({'operation': 'copy', 'password': 'invented'})
        self.assertEqual(error.exception.kind, 'clipboard')
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[1].args[0], ['/usr/bin/wl-paste', '--no-newline'])

    def test_clear_only_if_unchanged(self):
        for current, count in ((b'invented', 2), (b'changed', 1)):
            with patch.object(bridge.time, 'sleep'), patch.object(bridge, 'run', side_effect=[current, b'']) as run:
                bridge.clear_later(b'invented', 45)
            self.assertEqual(run.call_count, count)
            if count == 2:
                self.assertEqual(run.call_args.args[0], ['/usr/bin/wl-copy', '--clear'])

    def test_bounded_stdout_and_stderr(self):
        for descriptor in (1, 2):
            with self.subTest(descriptor=descriptor), self.assertRaises(bridge.Failure) as error:
                bridge.run(['/usr/bin/python3', '-I', '-S', '-c',
                            f'import os; os.write({descriptor}, b"x" * 100000)'])
            self.assertEqual(error.exception.kind, 'overflow')

    def test_detached_clipboard_owner_does_not_hold_response_pipes(self):
        code = 'import os,time; os.read(0,4096); child=os.fork(); time.sleep(0.5) if child == 0 else None; os._exit(0)'
        started = time.monotonic()
        bridge.run(['/usr/bin/python3', '-I', '-S', '-c', code], b'invented', timeout=0.2, capture=False)
        self.assertLess(time.monotonic() - started, 0.2)

    def test_clearer_handoff_timeout_reaps_child(self):
        child = subprocess.Popen(['/usr/bin/python3', '-I', '-S', '-c', 'import time; time.sleep(5)'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        with self.assertRaises(bridge.Failure) as error:
            bridge.handoff(child, b'x' * 1048576, timeout=0.05)
        self.assertEqual(error.exception.kind, 'timeout')
        self.assertIsNotNone(child.poll())
        self.assertTrue(child.stdin.closed)

    def test_timeout(self):
        with self.assertRaises(bridge.Failure) as error:
            bridge.run(['/usr/bin/python3', '-I', '-S', '-c', 'import time; time.sleep(5)'], timeout=0.05)
        self.assertEqual(error.exception.kind, 'timeout')

    def test_missing_and_error_do_not_echo_secrets(self):
        with self.assertRaises(bridge.Failure) as error:
            bridge.run(['/nonexistent/mint'])
        self.assertEqual(error.exception.kind, 'missing')
        with self.assertRaises(bridge.Failure) as error:
            bridge.run(['/usr/bin/python3', '-I', '-S', '-c', 'import sys; print("secret", file=sys.stderr); sys.exit(1)'])
        self.assertEqual(error.exception.kind, 'failed')
        self.assertNotIn('secret', str(error.exception))

    def test_external_stub_and_op_override(self):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory) / 'stub'
            stub.write_text('#!/usr/bin/python3 -I\nimport json,sys\nassert sys.argv[1:]==["vault","list","--format","json"]\nprint(json.dumps([{"id":"fake-id","name":"Invented"}]))\n')
            stub.chmod(0o700)
            proc = subprocess.run(['/usr/bin/python3', '-I', '-S', str(BRIDGE)],
                                  input=b'{"operation":"vaults"}', stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env={**os.environ, 'MINT_OP': str(stub)}, timeout=5)
        self.assertEqual(proc.stderr, b'')
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'data': [{'id': 'fake-id', 'name': 'Invented'}]})

    def test_malformed_command_json_has_no_secret(self):
        with patch.object(bridge, 'run', return_value=b'bad invented-secret'):
            with self.assertRaises(bridge.Failure) as error:
                bridge.dispatch({'operation': 'generate'})
        self.assertEqual(error.exception.kind, 'response')
        self.assertNotIn('invented-secret', str(error.exception))

    def test_request_limit_and_static_failure(self):
        for data, kind in ((b'x' * 65537, 'overflow'), (b'invalid invented-secret', 'response')):
            proc = subprocess.run(['/usr/bin/python3', '-I', '-S', str(BRIDGE)], input=data,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            result = json.loads(proc.stdout)
            self.assertEqual(result['kind'], kind)
            self.assertNotIn('invented-secret', proc.stdout.decode())
            self.assertEqual(proc.stderr, b'')

    def test_hostile_environment_removed(self):
        with patch.dict(os.environ, {'PATH': '/evil', 'PYTHONPATH': '/evil', 'LD_PRELOAD': '/evil'}):
            env = bridge.environment()
        self.assertEqual(env['PATH'], '/usr/bin:/bin')
        self.assertNotIn('PYTHONPATH', env)
        self.assertNotIn('LD_PRELOAD', env)

if __name__ == '__main__':
    unittest.main()
