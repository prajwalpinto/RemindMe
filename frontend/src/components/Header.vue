<template>
  <header class="app-header">
    <h1>RemindMe</h1>
    <nav>
      <router-link to="/" class="nav-button">Today</router-link>
      <router-link to="/week" class="nav-button">Week</router-link>
      <router-link to="/month" class="nav-button">Month</router-link>
      <router-link to="/all" class="nav-button">All Events</router-link>
      <router-link to="/event/new" class="nav-button create-button"
        >+ New Event</router-link
      >
    </nav>
    <div class="date-navigation">
      <!-- These buttons are illustrative. For full functionality, they would need to update the date in the router query params or a global state, and views would react to it. -->
      <button @click="navigateDay(-1)" class="nav-button">&lt; Prev Day</button>
      <span class="current-date">{{ formattedCurrentDate }}</span>
      <button @click="navigateDay(1)" class="nav-button">Next Day &gt;</button>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const currentDate = ref(new Date()); // This will track the date for day navigation

// Initialize date from URL if present
watch(
  () => route.query.date,
  (newDate) => {
    if (newDate) {
      currentDate.value = new Date(newDate + 'T00:00:00');
    } else {
      currentDate.value = new Date();
    }
  },
  { immediate: true },
);

const formattedCurrentDate = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
});

const navigateDay = (offset) => {
  const newDate = new Date(currentDate.value);
  newDate.setDate(newDate.getDate() + offset);
  currentDate.value = newDate;

  // Push to URL so views can react
  const isoDate = currentDate.value.toISOString().split('T')[0];
  router.push({ query: { ...route.query, date: isoDate } });
};
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px; /* Added for better spacing on smaller screens */
}

.app-header h1 {
  margin: 0;
  color: #333;
  flex-shrink: 0; /* Prevent h1 from shrinking */
}

.app-header nav {
  display: flex;
  gap: 10px;
  flex-grow: 1; /* Allow nav to take available space */
  justify-content: flex-start;
}

.nav-button {
  padding: 8px 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-decoration: none;
  color: #333;
  background-color: #f9f9f9;
  transition: background-color 0.2s ease;
  white-space: nowrap; /* Prevent text wrapping */
}

.nav-button:hover {
  background-color: #e9e9e9;
}

.nav-button.router-link-active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.create-button {
  background-color: #28a745;
  color: white;
  border-color: #28a745;
}

.create-button:hover {
  background-color: #218838;
}

.date-navigation {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0; /* Prevent date navigation from shrinking */
}

.current-date {
  font-weight: bold;
  font-size: 1.1em;
  white-space: nowrap;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .app-header nav {
    width: 100%;
    justify-content: space-around;
    margin-bottom: 10px;
  }
  .date-navigation {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
