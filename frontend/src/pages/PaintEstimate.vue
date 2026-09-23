<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'

const room_id = ref(1)
const ceilingEnabled = ref(false)
const ceilingCoverage = ref('')
const ceilingCoats = ref('')
const out = ref(null)
const err = ref('')
const busy = ref(false)

const numericOrUndef = (v) => {
  const s = String(v).trim()
  return s === '' ? undefined : Number(s)
}

const run = async () => {
  err.value = ''
  out.value = null
  busy.value = true
  try {
    const body = { room_id: room_id.value, persist: true, ceiling_enabled: ceilingEnabled.value }
    if (ceilingEnabled.value) {
      const cov = numericOrUndef(ceilingCoverage.value)
      const coats = numericOrUndef(ceilingCoats.value)
      if (cov !== undefined) body.ceiling_coverage = cov
      if (coats !== undefined) body.ceiling_coats = coats
    }
    out.value = await postJSON('/api/estimate', body)
  } catch (e) {
    err.value = friendly(e)
  } finally {
    busy.value = false
  }
}

const friendly = (e) => {
  try {
    const d = JSON.parse(e.message)
    const first = d.detail?.[0]
    if (first) return `入参非法：${first.loc?.join('.') || '参数'} ${first.msg || ''}`.trim()
  } catch (_) { /* plain text error */ }
  return e.message || '估算失败'
}
</script>

<template>
  <div class="page">
    <h1>估漆工作台</h1>
    <label>房间ID <input v-model.number="room_id" type="number" min="1" /></label>

    <label class="switch">
      <input type="checkbox" v-model="ceilingEnabled" />
      启用天花漆（独立涂布率与遍数）
    </label>

    <div v-if="ceilingEnabled" class="sub">
      <label>天花涂布率 m²/L（留空用默认）
        <input v-model="ceilingCoverage" type="number" min="0" step="0.1" placeholder="默认" />
      </label>
      <label>天花遍数（留空用默认）
        <input v-model="ceilingCoats" type="number" min="1" step="1" placeholder="默认" />
      </label>
    </div>

    <button :disabled="busy" @click="run">{{ busy ? '估算中…' : '估算并记录' }}</button>

    <p v-if="err" class="err">{{ err }}</p>

    <div v-if="out" class="result">
      <div class="stat">
        <h2>墙面</h2>
        <p>净面积 {{ out.net_m2 }} m²</p>
        <p class="hero-num">{{ out.liters }} L</p>
        <p>{{ out.coats }} 遍 · 涂布率 {{ out.coverage }} m²/L</p>
      </div>
      <div v-if="out.ceiling_enabled" class="stat">
        <h2>天花</h2>
        <p>天花面积 {{ out.ceiling_m2 }} m²</p>
        <p class="hero-num">{{ out.ceiling_liters }} L</p>
        <p>{{ out.ceiling_coats }} 遍 · 涂布率 {{ out.ceiling_coverage }} m²/L</p>
      </div>
      <div v-if="out.ceiling_enabled" class="stat total">
        <h2>合计</h2>
        <p class="hero-num">{{ out.total_liters }} L</p>
        <p>记录 #{{ out.run_id }}</p>
      </div>
      <p v-else>记录 #{{ out.run_id }}（仅墙面）</p>
    </div>
  </div>
</template>
