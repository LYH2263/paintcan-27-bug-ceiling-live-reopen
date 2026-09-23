<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'

const route = useRoute()
const detail = ref(null)
const est = ref(null)
const ceilingEnabled = ref(false)
const busy = ref(false)

const estimate = async () => {
  busy.value = true
  try {
    est.value = await postJSON('/api/estimate', {
      room_id: +route.params.id,
      persist: false,
      ceiling_enabled: ceilingEnabled.value,
    })
  } finally {
    busy.value = false
  }
}

const toggleCeiling = async () => { await estimate() }

const load = async () => {
  detail.value = await getJSON(`/api/rooms/${route.params.id}`)
  await estimate()
}
onMounted(load)
watch(() => route.params.id, load)
</script>

<template>
  <div class="page" v-if="detail">
    <h1>{{ detail.room.name }}</h1>
    <p>{{ detail.room.length }} × {{ detail.room.width }} × {{ detail.room.height }} m</p>

    <label class="switch">
      <input type="checkbox" v-model="ceilingEnabled" @change="toggleCeiling" :disabled="busy" />
      计入天花漆
    </label>

    <div v-if="est" class="result">
      <div class="stat">
        <h2>墙面</h2>
        <p>净面积 {{ est.net_m2 }} m²</p>
        <p class="hero-num">{{ est.liters }} L</p>
        <p>{{ est.coats }} 遍</p>
      </div>
      <div v-if="est.ceiling_enabled" class="stat">
        <h2>天花</h2>
        <p>天花面积 {{ est.ceiling_m2 }} m²</p>
        <p class="hero-num">{{ est.ceiling_liters }} L</p>
        <p>{{ est.ceiling_coats }} 遍</p>
      </div>
      <div v-if="est.ceiling_enabled" class="stat total">
        <h2>合计</h2>
        <p class="hero-num">{{ est.total_liters }} L</p>
      </div>
    </div>

    <h2>洞口</h2>
    <ul><li v-for="o in detail.openings" :key="o.id">{{ o.kind }} {{ o.w }}×{{ o.h }}</li></ul>
  </div>
</template>
