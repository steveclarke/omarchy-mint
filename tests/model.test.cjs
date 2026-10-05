const {test}=require('node:test');const assert=require('node:assert/strict');const M=require('../Model.js');
test('preferences clamp hostile settings and honor CLI strings',()=>{assert.equal(M.preferences({clearAfter:'0'}).clearAfter,0);assert.equal(M.preferences({clearAfter:Infinity}).clearAfter,45);assert.equal(M.preferences({clearAfter:900000}).clearAfter,3600)});
test('password response needs bounded explicit metadata',()=>{assert.throws(()=>M.password({password:'x',length:1,entropy_bits:Infinity}));assert.throws(()=>M.password({password:'x\n',length:2,entropy_bits:1}));assert.equal(M.password({password:'<>&',length:3,entropy_bits:4}).password,'<>&')});
test('metadata strips markup while option identity stays exact',()=>{assert.equal(M.clean('<b>abc&'), 'babc');assert.deepEqual(M.options([{name:'a&b'}],'preset'),[{value:'a&b',label:'ab'}])});
test('oversized malformed responses fail closed',()=>{assert.throws(()=>M.parse('x'.repeat(65537)));assert.throws(()=>M.parse('{}'));assert.throws(()=>M.options(Array(257).fill({name:'x'}),'preset'))});

test('default settings preserve exact identifiers',()=>{assert.equal(M.preferences({defaultPreset:'a&b',defaultVault:'a<b'}).defaultPreset,'a&b');assert.equal(M.preferences({defaultVault:'a<b'}).defaultVault,'a<b')});

test('DEL C1 and bidi controls never enter labels identities or passwords',()=>{
  for (const n of [0x7f,0x80,0x9f,0x61c,0x200e,0x200f,0x202a,0x202e,0x2066,0x2069]) {
    const value='a'+String.fromCharCode(n)+'b';
    assert.equal(M.clean(value),'ab');
    assert.equal(M.preferences({defaultPreset:value,defaultVault:value}).defaultPreset,'');
    assert.equal(M.preferences({defaultVault:value}).defaultVault,'');
    assert.throws(()=>M.password({password:value,length:3,entropy_bits:1}));
    assert.throws(()=>M.options([{name:value}],'preset'));
    assert.throws(()=>M.options([{id:value,name:'Example'}],'vault'));
  }
});
