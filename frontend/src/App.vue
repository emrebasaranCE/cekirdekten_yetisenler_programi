<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/map">Map</router-link> |
      <router-link to="/alerts">Alerts</router-link> |
      <router-link to="/analytics">Analytics</router-link> | 
      <router-link to="/charts">Charts</router-link>
    </nav>
    <!-- This is where your pages will appear -->
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
nav {
  padding: 1rem;
  background: #eef;
}
nav a {
  margin: 0 .5rem;
  text-decoration: none;
  color: #00f;
}
</style>
