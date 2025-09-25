<template>
	<div class="bg-surface-cards border border-outline-gray-1 rounded-lg p-6">
		<div class="mb-8 flex items-center justify-between">
			<h3 class="text-lg font-semibold text-ink-gray-9">{{ event.title }}</h3>

			<Button
				:link="`/events/${event.route}`"
				icon-left="external-link"
				variant="subtle"
				size="sm"
				>Visit Event Page
			</Button>
		</div>

		<div class="space-y-3">
			<!-- Date & Time -->
			<div class="flex justify-between items-center text-ink-gray-7">
				<span class="flex items-center">
					<LucideCalendarDays class="w-4 h-4 mr-2 flex-shrink-0" />
					Date & Time
				</span>
				<div class="text-right">
					<p class="font-medium text-ink-gray-9">{{ formatDate(event.start_date) }}</p>
					<p v-if="event.start_time" class="text-sm text-ink-gray-6">
						{{ formatTime(event.start_time) }}
						<span v-if="event.time_zone" class="text-ink-gray-5">
							({{ formatTimezone(event.time_zone) }})
						</span>
					</p>
				</div>
			</div>

			<!-- Venue -->
			<div v-if="event.venue" class="flex justify-between items-center text-ink-gray-7">
				<span class="flex items-center">
					<LucideMapPin class="w-4 h-4 mr-2 flex-shrink-0" />
					Venue
				</span>
				<div class="text-right">
					<p class="font-medium text-ink-gray-9">{{ event.venue }}</p>
				</div>
			</div>

			<!-- Event Description -->
			<div v-if="event.short_description" class="pt-2 border-t border-outline-gray-1">
				<p class="text-sm text-ink-gray-6">{{ event.short_description }}</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import LucideCalendarDays from "~icons/lucide/calendar-days";
import LucideMapPin from "~icons/lucide/map-pin";
import { dayjsLocal } from "frappe-ui";

defineProps({
	event: {
		type: Object,
		required: true,
		validator: (value) => {
			return (
				typeof value.title === "string" &&
				value.start_date &&
				typeof value.route === "string"
			);
		},
	},
});

const formatDate = (dateString) => {
	if (!dateString) return "";
	return dayjsLocal(dateString).format("dddd, MMMM D, YYYY");
};

const formatTime = (timeString) => {
	if (!timeString) return "";
	// Use a fixed date with the time string for parsing
	const dt = dayjsLocal(`2000-01-01T${timeString}`);
	return dt.format("h:mm A");
};

const formatTimezone = (timezone) => {
	if (!timezone) return "";
	try {
		const now = new Date();
		const abbreviation = new Intl.DateTimeFormat("en", {
			timeZone: timezone,
			timeZoneName: "short",
		})
			.formatToParts(now)
			.find((part) => part.type === "timeZoneName")?.value;

		return abbreviation || timezone.split("/")[1]?.replace("_", " ");
	} catch (error) {
		// Fallback to just the city name if timezone parsing fails
		return timezone.split("/")[1]?.replace("_", " ") || timezone;
	}
};
</script>
