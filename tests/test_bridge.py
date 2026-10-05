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
# Tests replace constants in the imported module, never production environment hooks.
bridge.OP = '/usr/bin/false'
os.environ['MINT_OP'] = '/usr/bin/false'


class BridgeTests(unittest.TestCase):
    def test_generation_options_no_shell(self):
        with patch.object(bridge, 'run', return_value=b'{"password":"invented"}') as run:
            result = bridge.dispatch({'operation': 'generate', 'length': '10-16',
                                      'classes': ['lower', 'digits'], 'symbols': '!$()', 'noAmbiguous': True})
        self.assertEqual(result['password'], 'invented')
        self.assertEqual(run.call_args.args[0][1:], ['--json', '10-16', '--no-upper', '--no-symbols', '--no-ambiguous'])

    def test_save_new_password_no_existing_secret(self):
        with patch.object(bridge, 'run', side_effect=[b'{"password":"new"}', b'{"copied":true,"clears_after":45}']) as run:
            bridge.dispatch({'operation': 'save', 'title': '--item=other', 'vault': 'Test', 'length': 24})
        args = run.call_args_list[0].args[0]
        self.assertIn('--title=--item=other', args)
        self.assertEqual(args[1:3], ['save', '--show'])
        self.assertNotIn('--copy', args)
        with self.assertRaises(bridge.Failure):
            bridge.dispatch({'operation': 'save', 'title': 'Test', 'password': 'existing'})

    def test_save_sensitive_copy_failure_preserves_saved_result(self):
        with patch.object(bridge, 'run', side_effect=[b'{"password":"new-invented","id":"fake-id"}', bridge.Failure('failed')]) as run:
            result = bridge.dispatch({'operation': 'save', 'title': 'Example', 'clearAfter': 0})
        self.assertEqual(result, {'password': 'new-invented', 'id': 'fake-id', 'copied': False})
        self.assertEqual(run.call_args_list[0].kwargs['timeout'], 120)
        self.assertEqual(run.call_args_list[1].args, ([bridge.MINT, 'copy', '--json', '--clear-after', '0'], b'new-invented'))
        self.assertEqual(run.call_count, 2)

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

    def test_copy_secret_only_stdin_through_mint(self):
        with patch.object(bridge, 'run', return_value=b'{"copied":true,"clears_after":45}') as run:
            result = bridge.dispatch({'operation': 'copy', 'password': 'invented-secret'})
        self.assertEqual(result, {'copied': True, 'clears_after': 45})
        self.assertEqual(run.call_args.args, ([bridge.MINT, 'copy', '--json', '--clear-after', '45'], b'invented-secret'))
        self.assertEqual(run.call_args.kwargs['timeout'], 35)

    def test_zero_delay_uses_mint_policy(self):
        with patch.object(bridge, 'run', return_value=b'{"copied":true,"clears_after":null}') as run:
            result = bridge.dispatch({'operation': 'copy', 'password': 'invented', 'clearAfter': 0})
        self.assertEqual(result, {'copied': True, 'clears_after': None})
        self.assertEqual(run.call_args.args[0][-1], '0')

    def test_sensitive_failure_has_no_fallback(self):
        with patch.object(bridge, 'run', side_effect=bridge.Failure('failed')) as run:
            with self.assertRaises(bridge.Failure) as error:
                bridge.dispatch({'operation': 'copy', 'password': 'invented'})
        self.assertEqual(error.exception.kind, 'failed')
        self.assertEqual(run.call_count, 1)

    def test_copy_preserves_bridge_failure_classes(self):
        kinds = ('missing', 'timeout', 'overflow', 'failed', 'response', 'clipboard',
                 'usage', 'unsatisfiable', 'onepassword')
        for kind in kinds:
            with self.subTest(kind=kind), patch.object(bridge, 'run', side_effect=bridge.Failure(kind)) as run:
                with self.assertRaises(bridge.Failure) as error:
                    bridge.dispatch({'operation': 'copy', 'password': 'invented-secret'})
                self.assertEqual(error.exception.kind, kind)
                self.assertTrue(run.call_args.kwargs['mint_errors'])
                self.assertEqual(run.call_count, 1)
        self.assertEqual(len({bridge.MESSAGES[kind] for kind in kinds}), len(kinds))
        self.assertNotIn('wl-clipboard', bridge.MESSAGES['missing'])

    def test_copy_invalid_success_response_is_distinct(self):
        for raw in (b'invented-secret', b'{}', b'{"copied":false}', b'{"copied":true,"clears_after":99}'):
            with self.subTest(raw=raw), patch.object(bridge, 'run', return_value=raw):
                with self.assertRaises(bridge.Failure) as error:
                    bridge.dispatch({'operation': 'copy', 'password': 'invented-secret'})
                self.assertEqual(error.exception.kind, 'response')
                self.assertNotIn('invented-secret', str(error.exception))

    def test_mint_json_stderr_maps_only_known_kind_code_pairs(self):
        for kind, code in (('usage', 2), ('unsatisfiable', 3), ('onepassword', 4), ('clipboard', 5)):
            with self.subTest(kind=kind):
                raw = json.dumps({'kind': kind, 'code': code, 'error': 'invented-secret <img>'})
                command = ['/usr/bin/python3', '-I', '-S', '-c',
                           'import sys; sys.stderr.write(sys.stdin.read()); sys.exit(int(sys.argv[1]))', str(code)]
                with self.assertRaises(bridge.Failure) as error:
                    bridge.run(command, raw.encode(), mint_errors=True)
                self.assertEqual(error.exception.kind, kind)
                self.assertNotIn('invented-secret', str(error.exception))
                self.assertNotIn('invented-secret', bridge.MESSAGES[error.exception.kind])
        for raw in (b'[]', b'invented-secret', b'{"kind":[],"code":5}',
                    b'{"kind":"invented-secret","code":5}', b'{"kind":"clipboard","code":2}',
                    b'{"kind":"clipboard","code":true}', b'{"kind":"clipboard","code":5.0}'):
            self.assertEqual(bridge.mint_failure(raw, 5), 'failed')
        self.assertEqual(bridge.mint_failure(b'{"kind":"clipboard","code":5}', 2), 'failed')

    def test_missing_mint_copy_runs_no_clipboard_fallback(self):
        with patch.object(bridge, 'MINT', '/nonexistent/mint-test/mint'):
            with self.assertRaises(bridge.Failure) as error:
                bridge.dispatch({'operation': 'copy', 'password': 'invented-secret'})
        self.assertEqual(error.exception.kind, 'missing')

    def test_control_classes_rejected_before_commands(self):
        controls = [0, 31, 127, 128, 159, 0x61c, 0x200e, 0x200f, 0x202a, 0x202e, 0x2066, 0x2069]
        for code in controls:
            for key in ('title', 'vault', 'url', 'username'):
                with self.subTest(code=code, key=key), patch.object(bridge, 'run') as run:
                    with self.assertRaises(bridge.Failure):
                        bridge.dispatch({'operation': 'save', 'title': 'Example', key: 'a' + chr(code) + 'b'})
                    run.assert_not_called()

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

    def test_external_stub_with_test_only_source_substitution(self):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory) / 'stub'
            stub.write_text('#!/usr/bin/python3 -I\nimport json,sys\nassert sys.argv[1:]==["vault","list","--format","json"]\nprint(json.dumps([{"id":"fake-id","name":"Invented"}]))\n')
            stub.chmod(0o700)
            fixture = Path(directory) / 'bridge'
            source = BRIDGE.read_text()
            assignment = 'OP = "/usr/bin/op"'
            self.assertEqual(source.count(assignment), 1, 'Test must replace exactly one production OP constant')
            source = source.replace(assignment, 'OP = ' + repr(str(stub)))
            self.assertNotIn('/usr/bin/op', source, 'Fixture must never retain the real op executable')
            fixture.write_text(source)
            proc = subprocess.run(['/usr/bin/python3', '-I', '-S', str(fixture)], input=b'{"operation":"vaults"}', stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env={**os.environ, 'MINT_OP': str(stub)}, timeout=5)
        self.assertEqual(proc.stderr, b'')
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'data': [{'id': 'fake-id', 'name': 'Invented'}]})

    def test_executable_overrides_ignored_and_resolved_op_forwarded(self):
        with patch.dict(os.environ, {'MINT_OP': '/evil/op', 'MINT_BINARY': '/evil/mint', 'PATH': '/evil'}):
            with patch.object(bridge, 'run', return_value=b'[]') as run:
                bridge.dispatch({'operation': 'vaults'})
            self.assertEqual(run.call_args.args[0][0], bridge.OP)
            self.assertEqual(bridge.environment()['MINT_OP'], bridge.OP)
            self.assertNotIn('MINT_BINARY', bridge.environment())
            with patch.object(bridge, 'run', return_value=b'{"password":"fixture"}') as run:
                bridge.dispatch({'operation': 'generate'})
            self.assertEqual(run.call_args.args[0][0], '/usr/bin/mint')

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
