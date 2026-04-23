import { createRouter, createWebHistory } from 'vue-router';
import TodayView from '../views/TodayView.vue';
import WeekView from '../views/WeekView.vue';
import MonthView from '../views/MonthView.vue';
import EventForm from '../components/EventForm.vue';
import AllEventsView from '../views/AllEventsView.vue';

const routes = [
  {
    path: '/',
    name: 'Today',
    component: TodayView,
    meta: { title: 'Today' },
  },
  {
    path: '/week',
    name: 'Week',
    component: WeekView,
    meta: { title: 'This Week' },
  },
  {
    path: '/month',
    name: 'Month',
    component: MonthView,
    meta: { title: 'This Month' },
  },
  {
    path: '/all',
    name: 'AllEvents',
    component: AllEventsView,
    meta: { title: 'All Events' },
  },
  {
    path: '/event/new',
    name: 'NewEvent',
    component: EventForm,
    meta: { title: 'New Event' },
  },
  {
    path: '/event/edit/:id',
    name: 'EditEvent',
    component: EventForm,
    props: true, // Allows passing route params as props to the component
    meta: { title: 'Edit Event' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Update document title based on route meta
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `RemindMe - ${to.meta.title}` : 'RemindMe';
  next();
});

export default router;
