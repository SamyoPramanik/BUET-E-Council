<template>
  <div class="container mx-auto py-8 px-4">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="hidden lg:block lg:col-span-1"></div>

      <div class="col-span-1 lg:col-span-10">
        <header class="mb-8">
          <h1 class="text-3xl font-bold text-slate-800 tracking-tight">Council Meetings</h1>
          <p class="text-slate-500">Access and manage Academic and Syndicate records</p>
        </header>

        <div class="flex space-x-1 bg-slate-200/60 p-1 rounded-xl mb-6 w-full sm:w-72 border border-slate-200">
          <button 
            @click="setTab(true)"
            :class="[isAcademic ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:text-slate-800']"
            class="flex-1 py-2 text-sm font-semibold rounded-lg transition-all"
          >
            Academic
          </button>
          <button 
            @click="setTab(false)"
            :class="[!isAcademic ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:text-slate-800']"
            class="flex-1 py-2 text-sm font-semibold rounded-lg transition-all"
          >
            Syndicate
          </button>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <table class="w-full text-left border-collapse table-fixed">
            <thead class="bg-slate-50/80 border-b border-slate-200">
              <tr>
                <th @click="toggleSort('serial_num')" class="p-4 w-24 cursor-pointer hover:bg-slate-100 transition">
                  <div class="flex items-center space-x-1">
                    <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Serial</span>
                    <span v-if="sortBy === 'serial_num'" class="text-blue-500 text-xs">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="p-4">
                  <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Title</span>
                </th>
                <th class="p-4 w-32 text-center">
                  <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Status</span>
                </th>
                <th @click="toggleSort('meeting_date')" class="p-4 w-40 cursor-pointer hover:bg-slate-100 transition">
                  <div class="flex items-center justify-end space-x-1">
                    <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Meeting Date</span>
                    <span v-if="sortBy === 'meeting_date'" class="text-blue-500 text-xs">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-100">
              <tr v-for="meeting in meetings" :key="meeting.id" class="hover:bg-slate-50/50 transition-colors group">
                <td class="p-4">
                 <router-link 
                  :to="{ name: 'MeetingDetails', params: { id: meeting.id }}"
                  class="font-mono font-bold text-blue-600 hover:underline"
                >
                  #{{ meeting.serial_num }}
                </router-link>
                </td>

                <td class="p-4">
                  <p class="text-slate-700 font-medium truncate" :title="meeting.title_plain">
                    {{ meeting.title_plain }}
                  </p>
                </td>

                <td class="p-4 text-center">
                  <span 
                    v-if="meeting.is_finished" 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200"
                  >
                    Finished
                  </span>
                  <span 
                    v-else 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200"
                  >
                    Ongoing
                  </span>
                </td>

                <td class="p-4 text-right text-slate-500 text-sm font-medium">
                  {{ new Date(meeting.meeting_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) }}
                </td>
              </tr>

              <tr v-if="loading">
                <td colspan="4" class="p-12 text-center">
                  <div class="flex flex-col items-center gap-2">
                    <div class="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <span class="text-sm text-slate-400 font-medium tracking-wide">Fetching meetings...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="meetings.length === 0">
                <td colspan="4" class="p-12 text-center text-slate-400 italic">
                  No meeting records found for this category.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-slate-500 font-medium">
            Showing <span class="text-slate-800">{{ meetings.length }}</span> of <span class="text-slate-800">{{ totalCount }}</span> records
          </p>
          <div class="flex items-center space-x-2">
            <button 
              @click="changePage(currentPage - 1)" 
              :disabled="currentPage === 1 || loading"
              class="px-4 py-2 text-sm font-semibold border rounded-xl disabled:opacity-40 hover:bg-white hover:shadow-sm transition-all bg-slate-50"
            >
              Previous
            </button>
            <div class="px-4 py-2 text-sm font-bold bg-white border rounded-xl shadow-sm text-blue-600">
              {{ currentPage }}
            </div>
            <button 
              @click="changePage(currentPage + 1)" 
              :disabled="currentPage * 10 >= totalCount || loading"
              class="px-4 py-2 text-sm font-semibold border rounded-xl disabled:opacity-40 hover:bg-white hover:shadow-sm transition-all bg-slate-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <div class="hidden lg:block lg:col-span-1"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../utils/api' 

const meetings = ref([])
const totalCount = ref(0)
const loading = ref(false)
const isAcademic = ref(true)
const currentPage = ref(1)
const sortBy = ref('meeting_date')
const sortDir = ref('desc')

const fetchMeetings = async () => {
  loading.value = true
  try {
    const response = await api.get('/meetings/', {
      params: {
        is_academic: isAcademic.value,
        page: currentPage.value,
        limit: 10
      }
    })
    meetings.value = response.data.data
    totalCount.value = response.data.total_count
  } catch (error) {
    console.error("Failed to fetch meetings", error)
  } finally {
    loading.value = false
  }
}

const setTab = (val) => {
  if (isAcademic.value === val) return
  isAcademic.value = val
  currentPage.value = 1
}

const changePage = (page) => {
  currentPage.value = page
}

const toggleSort = (column) => {
  if (sortBy.value === column) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortDir.value = 'asc'
  }
  
  // Frontend local sort for immediate feedback
  meetings.value.sort((a, b) => {
    let modifier = sortDir.value === 'asc' ? 1 : -1
    if (a[column] < b[column]) return -1 * modifier
    if (a[column] > b[column]) return 1 * modifier
    return 0
  })
}

watch([isAcademic, currentPage], fetchMeetings)
onMounted(fetchMeetings)
</script>

<style scoped>
/* Optional: Handle table header text wrap issues */
th {
  white-space: nowrap;
}
</style>