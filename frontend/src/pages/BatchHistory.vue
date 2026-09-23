<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const selected = ref(null)
const err = ref('')

onMounted(async () => { items.value = (await getJSON('/api/history')).items })

const open = async (id) => {
  err.value = ''
  try {
    selected.value = await getJSON(`/api/history/${id}`)
  } catch (e) {
    err.value = `记录 #${id} 不存在`
    selected.value = null
  }
}
</script>

<template>
  <div class="page">
    <h1>估算记录</h1>
    <table>
      <thead>
        <tr>
          <th>#</th><th>时间</th><th>房间</th>
          <th>墙面升数</th><th>天花升数</th><th>天花</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="h in items" :key="h.id" class="row" @click="open(h.id)">
          <td>#{{ h.id }}</td>
          <td>{{ h.created_at }}</td>
          <td>{{ h.room_id ?? '—' }}</td>
          <td>{{ h.result?.liters ?? '—' }}</td>
          <td>{{ h.result?.ceiling_liters ?? '—' }}</td>
          <td>{{ h.result?.ceiling_enabled ? '启用' : '关闭' }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="err" class="err">{{ err }}</p>

    <div v-if="selected" class="detail">
      <h2>记录 #{{ selected.id }}</h2>
      <p>时间 {{ selected.created_at }} · 房间 {{ selected.room_id }}</p>
      <ul>
        <li>墙面：{{ selected.result?.net_m2 }} m² →
          <strong>{{ selected.result?.liters }} L</strong>
          （{{ selected.result?.coats }} 遍 / {{ selected.result?.coverage }} m²/L）</li>
        <li v-if="selected.result?.ceiling_enabled || selected.live_reopen">
          天花：{{ selected.result.ceiling_m2 }} m² →
          <strong>{{ selected.result.ceiling_liters }} L</strong>
          （{{ selected.result.ceiling_coats }} 遍 / {{ selected.result.ceiling_coverage }} m²/L）
        </li>
        <li v-else>天花：关闭</li>
        <li v-if="selected.result?.ceiling_enabled || selected.result?.total_liters != null">
          合计：{{ selected.result.total_liters ?? selected.result.liters }} L
        </li>
      </ul>
    </div>
  </div>
</template>
