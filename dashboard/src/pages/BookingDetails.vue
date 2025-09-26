<template>
	<BookingHeader :booking-id="bookingId" />

	<div class="w-4" v-if="bookingDetails.loading">
		<Spinner />
	</div>

	<div v-else-if="bookingDetails.data">
		<!-- Success Message (only shown on payment success) -->
		<SuccessMessage :show="showSuccessMessage" />

		<!-- Event Information and Payment Summary in two columns -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
			<!-- Event Information -->
			<BookingEventInfo
				v-if="bookingDetails.data.event"
				:event="bookingDetails.data.event"
			/>

			<!-- Booking Financial Summary -->
			<BookingFinancialSummary
				v-if="bookingDetails.data.doc"
				:booking="bookingDetails.data.doc"
			/>

			<!-- Booking Financial Summary -->
			<BookingFinancialSummary
				v-if="bookingDetails.data.booking_summary"
				:summary="bookingDetails.data.booking_summary"
			/>
		</div>

		<!-- Cancellation Request Section -->
		<CancellationRequestNotice
			:cancellation-request="bookingDetails.data.cancellation_request"
		/>

		<!-- Tickets Section -->
		<TicketsSection
			:tickets="bookingDetails.data.tickets"
			:can-request-cancellation="canRequestCancellation"
			:can-transfer-tickets="canTransferTickets"
			:can-change-add-ons="canChangeAddOns"
			:cancellation-request="bookingDetails.data.cancellation_request"
			:cancelled-tickets="bookingDetails.data.cancelled_tickets"
			@request-cancellation="showCancellationDialog = true"
			@transfer-success="onTicketTransferSuccess"
		/>

		<CancellationRequestDialog
			v-model="showCancellationDialog"
			:tickets="bookingDetails.data.tickets"
			:booking-id="bookingId"
			@success="onCancellationRequestSuccess"
		/>
	</div>
</template>

<script setup>
import { ref, computed } from "vue";
import { createResource, Spinner } from "frappe-ui";
import { usePaymentSuccess } from "../composables/usePaymentSuccess.js";
import { useBookingFormStorage } from "../composables/useBookingFormStorage.js";
import BookingHeader from "../components/BookingHeader.vue";
import SuccessMessage from "../components/SuccessMessage.vue";
import CancellationRequestNotice from "../components/CancellationRequestNotice.vue";
import TicketsSection from "../components/TicketsSection.vue";
import CancellationRequestDialog from "../components/CancellationRequestDialog.vue";
import BookingFinancialSummary from "../components/BookingFinancialSummary.vue";
import BookingEventInfo from "../components/BookingEventInfo.vue";

const props = defineProps({
	bookingId: {
		type: String,
		required: true,
	},
});

// Use booking form storage composable to clear data on successful payment
const { clearStoredData } = useBookingFormStorage();

// Use payment success composable with callback to clear booking form data
const { showSuccessMessage } = usePaymentSuccess({
	onSuccess: () => {
		// Clear any stored booking form data when payment is successful
		clearStoredData();
	},
});

const showCancellationDialog = ref(false);

const bookingDetails = createResource({
	url: "buzz.api.get_booking_details",
	params: { booking_id: props.bookingId },
	auto: true,
});

const canTransferTickets = computed(() => {
	return bookingDetails.data?.can_transfer_ticket?.can_transfer || false;
});

const canChangeAddOns = computed(() => {
	return bookingDetails.data?.can_change_add_ons?.can_change_add_ons || false;
});

const canRequestCancellation = computed(() => {
	return bookingDetails.data?.can_request_cancellation?.can_request_cancellation || false;
});

const onTicketTransferSuccess = () => {
	bookingDetails.reload();
};

const onCancellationRequestSuccess = (data) => {
	bookingDetails.reload();
};
</script>
