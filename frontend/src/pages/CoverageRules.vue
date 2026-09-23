<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const s = ref({ coverage: 8, coats: 2, ceiling_coverage: 8, ceiling_coats: 2 })
const loaded = ref(false)
const saving = ref(false)
const msg = ref('')
const err = ref('')

onMounted(async () => {
  s.value = await getJSON('/api/settings')
  loaded.value = true
})

const save = async () => {
  msg.value = ''; err.value = ''
  saving.value = true
  try {
    s.value = await postJSON('/api/settings', {
      coverage: Number(s.value.coverage),
      coats: Number(s.value.coats),
      ceiling_coverage: Number(s.value.ceiling_coverage),
      ceiling_coats: Number(s.value.ceiling_coats),
    })
    msg.value = '已保存'
  } catch (e) {
    err.value = '保存失败：涂布率与遍数必须为正数。'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>遮盖力参数</h1>
    <div v-if="loaded" class="rules-grid">
      <fieldset>
        <legend>墙面默认</legend>
        <label>每升可刷 m² <input v-model.number="s.coverage" type="number" min="0" step="0.1" /></label>
        <label>默认遍数 <input v-model.number="s.coats" type="number" min="1" step="1" /></label>
      </fieldset>
      <fieldset>
        <legend>天花默认</legend>
        <label>每升可刷 m² <input v-model.number="s.ceiling_coverage" type="number" min="0" step="0.1" /></label>
        <label>默认遍数 <input v-model.number="s.ceiling_coats" type="number" min="1" step="1" /></label>
      </fieldset>
    </div>
    <button :disabled="saving || !loaded" @click="save">{{ saving ? '保存中…' : '保存' }}</button>
    <span v-if="msg" class="ok">{{ msg }}</span>
    <span v-if="err" class="err">{{ err }}</span>
  </div>
</template>
