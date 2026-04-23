<template>
  <div class="view-container">
    <h2>This Month's Events</h2>
    <div v-if="loading" class="loading-message">Loading events...</div>
    <div v-else-if="error" class="error-message">Error: {{ error }}</div>
    <div v-else-if="events.length === 0" class="no-events-message">
      No events for this month.
    </div>
    <div v-else class="event-list">
      <EventCard
        v-for="event in events"
        :key="event.id + '-' + event.start_date + '-' + event.start_time"
        :event="event"
        @event-updated="fetchEvents"
        @event-deleted="fetchEvents"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import EventCard from '../components/EventCard.vue';

const events = ref([]);
const loading = ref(true);
const error = ref(null);
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const fetchEvents = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await axios.get(`${API_BASE_URL}/events/month/`);
    events.value = response.data;
  } catch (err) {
    error.value = "Failed to fetch this month's events.";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchEvents);
</script>

<style scoped>
/* Reusing styles from TodayView.vue */
.view-container {
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.loading-message,
.error-message,
.no-events-message {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.loading-message {
  background-color: #e0f7fa;
  color: #007bff;
}
.error-message {
  background-color: #ffebee;
  color: #d32f2f;
}
.no-events-message {
  background-color: #f0f4c3;
  color: #689f38;
}

.event-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
</style>
