<template>
	<div>
		<div>
			<Navbar />
		</div>
		<div class="max-w-4xl py-8 px-4 md:py-12 mx-auto">
			<slot></slot>
		</div>
	</div>
</template>

<script setup>
import Navbar from "@/components/Navbar.vue";
</script>
