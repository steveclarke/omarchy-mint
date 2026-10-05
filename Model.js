function clean(value, cap) { return typeof value === 'string' ? value.replace(/[<>&\x00-\x1f\x7f]/g, '').slice(0, cap || 160) : '' }
function integer(value, fallback, min, max) { var n = Number(value); return Number.isFinite(n) ? Math.max(min, Math.min(max, Math.round(n))) : fallback }
function identity(value, cap) { return typeof value === 'string' && value.length <= cap && !/[\x00-\x1f\x7f]/.test(value) ? value : '' }
function preferences(entry) { return {clearAfter: integer(entry.clearAfter,45,0,3600), defaultPreset: identity(entry.defaultPreset,80), defaultVault: identity(entry.defaultVault,120)} }
function parse(raw) {
  if (typeof raw !== 'string' || raw.length > 65536) throw Error('size')
  var doc = JSON.parse(raw)
  if (!doc || typeof doc.ok !== 'boolean') throw Error('shape')
  if (!doc.ok) return {ok:false,kind:clean(doc.kind,40),error:clean(doc.error,240)}
  return doc
}
function password(data) {
  if (!data || typeof data.password !== 'string' || !data.password.length || data.password.length > 16384 || /[\x00-\x1f\x7f]/.test(data.password)) throw Error('password')
  if (!Number.isFinite(data.entropy_bits) || !Number.isInteger(data.length) || data.length < 1 || data.length > 16384) throw Error('metadata')
  return {password:data.password,length:data.length,entropy_bits:data.entropy_bits,rule:clean(data.rule && data.rule.summary,180)}
}
function options(data, kind) {
  if (!Array.isArray(data) || data.length > 256) throw Error('list')
  return data.map(function(v) { var raw = kind === 'vault' ? v.id : v.name; if(typeof raw !== 'string' || raw.length>120 || /[\x00-\x1f\x7f]/.test(raw)) throw Error('option'); var value=raw; return {value:value,label:clean(v.name,120)} }).filter(function(v){ return v.value && v.label })
}
if (typeof module !== 'undefined') module.exports = {clean,integer,preferences,parse,password,options}
