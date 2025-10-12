<template>
	<div class="border-b">
		<nav class="flex items-center justify-between gap-4 p-4 max-w-7xl mx-auto">
			<RouterLink :to="{ name: 'bookings-tab' }">
				<span class="font-bold text-ink-gray-7">Buzz</span>
			</RouterLink>
			<div class="flex items-center gap-2">
				<Button variant="ghost" size="md" @click="toggleTheme">
					<LucideSun v-if="userTheme === 'dark'" class="w-4 h-4" />
					<LucideMoon v-else class="w-4 h-4" />
				</Button>
				<Button @click="session.logout.submit" icon-right="log-out" variant="ghost" size="md">
					Log Out
				</Button>
			</div>
		</nav>
	</div>
</template>

<script setup>
import LucideSun from "~icons/lucide/sun";
import LucideMoon from "~icons/lucide/moon";
import { session } from "../data/session";

import { onMounted } from "vue";
import { useStorage } from "@vueuse/core";

const userTheme = useStorage("user-theme", "dark");

onMounted(() => {
	document.documentElement.setAttribute("data-theme", userTheme.value);
});

function toggleTheme() {
	const currentTheme = userTheme.value;
	const newTheme = currentTheme === "dark" ? "light" : "dark";
	document.documentElement.setAttribute("data-theme", newTheme);
	userTheme.value = newTheme;
}
</script>
