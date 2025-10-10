<template>
	<div>
		<div>
			<Navbar />
		</div>
		<div class="max-w-6xl py-8 md:py-12 mx-auto">
			<slot></slot>
		</div>
	</div>
</template>

<script setup>
import Navbar from "@/components/Navbar.vue";
</script>
