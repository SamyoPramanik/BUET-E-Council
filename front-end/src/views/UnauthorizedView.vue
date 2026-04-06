<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50">
    <h1 class="text-6xl font-black text-red-600">403</h1>
    <p class="text-xl font-bold text-gray-800 mt-4">Access Denied</p>
    <p class="text-gray-500 mb-8">You don't have permission to view the admin panel.</p>
    <router-link to="/profile" class="text-blue-600 font-bold hover:underline">
      Back to Profile
    </router-link>
  </div>
</template>