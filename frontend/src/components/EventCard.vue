<template>
  <div :class="['event-card', { 'is-completed': event.is_completed }]">
    <div class="event-header">
      <h3 class="event-title">{{ event.title }}</h3>
      <span class="event-type">{{ formatEventType(event.event_type) }}</span>
    </div>
    <p v-if="event.description" class="event-description">
      {{ event.description }}
    </p>
    <div class="event-details">
      <span v-if="event.start_date" class="event-date">
        {{ formatDate(event.start_date) }}
        <span v-if="!event.is_all_day && event.start_time">
          at {{ formatTime(event.start_time) }}</span
        >
        <span v-if="event.end_date && event.end_date !== event.start_date">
          - {{ formatDate(event.end_date) }}</span
        >
        <span
          v-if="
            !event.is_all_day &&
            event.end_time &&
            event.end_date === event.start_date
          "
        >
          - {{ formatTime(event.end_time) }}</span
        >
      </span>
      <span v-if="event.is_all_day" class="event-all-day">All Day</span>
      <span v-if="event.is_recurring" class="event-recurring">Recurring</span>
    </div>
    <div class="event-actions">
      <button @click="editEvent" class="action-button edit-button">Edit</button>
      <button
        @click="toggleComplete"
        v-if="event.event_type !== 'recurring'"
        class="action-button complete-button"
      >
        {{ event.is_completed ? 'Uncomplete' : 'Complete' }}
      </button>
      <button @click="deleteEvent" class="action-button delete-button">
        Delete
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['event-updated', 'event-deleted']);
const router = useRouter();
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const formatDate = (dateString) => {
  if (!dateString) return '';
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

const formatTime = (timeString) => {
  if (!timeString) return '';
  // Assuming timeString is in "HH:MM:SS" format from backend
  const [hours, minutes] = timeString.split(':');
  const date = new Date();
  date.setHours(parseInt(hours));
  date.setMinutes(parseInt(minutes));
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatEventType = (type) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
};

const editEvent = () => {
  router.push({ name: 'EditEvent', params: { id: props.event.id } });
};

const toggleComplete = async () => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/events/${props.event.id}/complete`,
    );
    emit('event-updated', response.data);
  } catch (error) {
    console.error('Error completing event:', error);
    alert('Failed to update event status.');
  }
};

const deleteEvent = async () => {
  if (confirm('Are you sure you want to delete this event?')) {
    try {
      await axios.delete(`${API_BASE_URL}/events/${props.event.id}`);
      emit('event-deleted', props.event.id);
    } catch (error) {
      console.error('Error deleting event:', error);
      alert('Failed to delete event.');
    }
  }
};
</script>

<style scoped>
.event-card {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease-in-out;
}

.event-card:hover {
  transform: translateY(-3px);
}

.event-card.is-completed {
  opacity: 0.7;
  text-decoration: line-through;
  background-color: #f0f0f0;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.event-title {
  margin: 0;
  color: #333;
  font-size: 1.2em;
}

.event-type {
  background-color: #e0f7fa;
  color: #007bff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
}

.event-description {
  color: #555;
  margin-bottom: 10px;
}

.event-details {
  font-size: 0.9em;
  color: #777;
  margin-bottom: 10px;
}

.event-all-day,
.event-recurring {
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  margin-left: 5px;
  font-size: 0.8em;
}

.event-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s ease;
}

.edit-button {
  background-color: #007bff;
  color: white;
}

.edit-button:hover {
  background-color: #0056b3;
}

.complete-button {
  background-color: #28a745;
  color: white;
}

.complete-button:hover {
  background-color: #218838;
}

.delete-button {
  background-color: #dc3545;
  color: white;
}

.delete-button:hover {
  background-color: #c82333;
}
</style>
