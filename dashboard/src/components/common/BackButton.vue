<template>
	<Button icon-left="chevron-left" :route="to">
		{{ label }}
	</Button>
</template>

<script setup>
const props = defineProps({
	to: {
		type: [String, Object],
		required: true,
	},
	label: {
		type: String,
		default: "Back",
	},
});
</script>
