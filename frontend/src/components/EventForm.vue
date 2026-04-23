<template>
  <div class="event-form-container">
    <h2>{{ isEditMode ? 'Edit Event' : 'Create New Event' }}</h2>
    <form @submit.prevent="handleSubmit" class="event-form">
      <div class="form-group">
        <label for="title">Title:</label>
        <input type="text" id="title" v-model="event.title" required />
      </div>

      <div class="form-group">
        <label for="description">Description:</label>
        <textarea id="description" v-model="event.description"></textarea>
      </div>

      <div class="form-group">
        <label for="event_type">Event Type:</label>
        <select id="event_type" v-model="event.event_type">
          <option value="task">Task</option>
          <option value="todo">Todo</option>
          <option value="birthday">Birthday</option>
          <option value="bill_payment">Bill Payment</option>
          <option value="recurring">Recurring Event</option>
        </select>
      </div>

      <div class="form-group checkbox-group">
        <input type="checkbox" id="is_all_day" v-model="event.is_all_day" />
        <label for="is_all_day">All Day Event</label>
      </div>

      <div class="form-group" v-if="!event.is_all_day">
        <label for="start_date">Start Date:</label>
        <input type="date" id="start_date" v-model="event.start_date" />
      </div>

      <div class="form-group" v-if="!event.is_all_day && event.start_date">
        <label for="start_time">Start Time:</label>
        <input type="time" id="start_time" v-model="event.start_time" />
      </div>

      <div class="form-group" v-if="!event.is_all_day && event.start_date">
        <label for="end_date">End Date:</label>
        <input type="date" id="end_date" v-model="event.end_date" />
      </div>

      <div class="form-group" v-if="!event.is_all_day && event.end_date">
        <label for="end_time">End Time:</label>
        <input type="time" id="end_time" v-model="event.end_time" />
      </div>

      <div class="form-group checkbox-group">
        <input type="checkbox" id="is_completed" v-model="event.is_completed" />
        <label for="is_completed">Completed</label>
      </div>

      <div class="form-group checkbox-group">
        <input type="checkbox" id="is_recurring" v-model="event.is_recurring" />
        <label for="is_recurring">Is Recurring?</label>
      </div>

      <div v-if="event.is_recurring" class="recurring-options">
        <p>
          Define Recurrence Pattern (e.g., "FREQ=WEEKLY;INTERVAL=2;BYDAY=SA")
        </p>
        <div class="form-group">
          <label for="recurrence_pattern">Pattern:</label>
          <input
            type="text"
            id="recurrence_pattern"
            v-model="event.recurrence_pattern"
            placeholder="FREQ=WEEKLY;INTERVAL=2;BYDAY=SA"
          />
        </div>
        <div class="form-group">
          <label for="recurrence_end_date"
            >Recurrence End Date (Optional):</label
          >
          <input
            type="date"
            id="recurrence_end_date"
            v-model="event.recurrence_end_date"
          />
        </div>
        <p class="help-text">
          Use
          <a
            href="https://dateutil.readthedocs.io/en/stable/rrule.html#rrule-string-format"
            target="_blank"
            >rrule format</a
          >. Example: "FREQ=WEEKLY;INTERVAL=2;BYDAY=SA" for every two weeks on
          Saturday. "FREQ=MONTHLY;BYMONTHDAY=15" for 15th of every month.
        </p>
      </div>

      <div class="form-actions">
        <button type="submit" class="submit-button">
          {{ isEditMode ? 'Update Event' : 'Create Event' }}
        </button>
        <button type="button" @click="router.back()" class="cancel-button">
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const isEditMode = computed(() => !!route.params.id);

const event = ref({
  title: '',
  description: '',
  event_type: 'task',
  start_date: null,
  start_time: null,
  end_date: null,
  end_time: null,
  is_all_day: false,
  is_completed: false,
  is_recurring: false,
  recurrence_pattern: null,
  recurrence_end_date: null,
});

// Watch for changes in is_all_day to clear time fields
watch(
  () => event.value.is_all_day,
  (newVal) => {
    if (newVal) {
      event.value.start_time = null;
      event.value.end_time = null;
    }
  },
);

onMounted(async () => {
  if (isEditMode.value) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/events/${route.params.id}`,
      );
      const fetchedEvent = response.data;
      // Format dates and times for HTML input fields
      event.value = {
        ...fetchedEvent,
        start_date: fetchedEvent.start_date
          ? new Date(fetchedEvent.start_date).toISOString().split('T')[0]
          : null,
        end_date: fetchedEvent.end_date
          ? new Date(fetchedEvent.end_date).toISOString().split('T')[0]
          : null,
        // Times are already in "HH:MM:SS" format from backend, which HTML time input handles
        recurrence_end_date: fetchedEvent.recurrence_end_date
          ? new Date(fetchedEvent.recurrence_end_date)
              .toISOString()
              .split('T')[0]
          : null,
      };
    } catch (error) {
      console.error('Error fetching event for edit:', error);
      alert('Failed to load event for editing.');
      router.push('/');
    }
  }
});

const handleSubmit = async () => {
  try {
    // Prepare data for API
    const payload = { ...event.value };

    // Ensure date/time fields are null if empty strings
    // HTML date/time inputs return empty string if cleared
    for (const key of ['start_date', 'end_date', 'recurrence_end_date']) {
      if (payload[key] === '') payload[key] = null;
    }
    for (const key of ['start_time', 'end_time']) {
      if (payload[key] === '') payload[key] = null;
    }

    let response;
    if (isEditMode.value) {
      response = await axios.put(
        `${API_BASE_URL}/events/${route.params.id}`,
        payload,
      );
      alert('Event updated successfully!');
    } else {
      response = await axios.post(`${API_BASE_URL}/events/`, payload);
      alert('Event created successfully!');
    }
    console.log(response.data);
    router.push('/'); // Navigate back to today's view
  } catch (error) {
    console.error(
      'Error saving event:',
      error.response ? error.response.data : error.message,
    );
    alert('Failed to save event. Check console for details.');
  }
};
</script>

<style scoped>
.event-form-container {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 20px auto;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 25px;
}

.event-form .form-group {
  margin-bottom: 15px;
}

.event-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.event-form input[type='text'],
.event-form input[type='date'],
.event-form input[type='time'],
.event-form textarea,
.event-form select {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1em;
  box-sizing: border-box; /* Include padding in width */
}

.event-form textarea {
  resize: vertical;
  min-height: 80px;
}

.event-form .checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.event-form .checkbox-group input[type='checkbox'] {
  margin-right: 10px;
  width: auto; /* Override default input width */
}

.event-form .checkbox-group label {
  margin-bottom: 0;
}

.recurring-options {
  background-color: #f9f9f9;
  border: 1px dashed #ddd;
  padding: 15px;
  border-radius: 5px;
  margin-top: 15px;
}

.recurring-options p {
  margin-top: 0;
  font-style: italic;
  color: #666;
}

.recurring-options .help-text {
  font-size: 0.9em;
  color: #888;
  margin-top: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
}

.submit-button,
.cancel-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.2s ease;
}

.submit-button {
  background-color: #007bff;
  color: white;
}

.submit-button:hover {
  background-color: #0056b3;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #5a6268;
}
</style>
