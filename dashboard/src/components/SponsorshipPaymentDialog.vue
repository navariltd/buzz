<template>
	<Dialog
		v-model="isOpen"
		:options="{
			title: 'Select Sponsorship Tier',
			size: 'xl',
			description: 'Choose your preferred sponsorship tier and proceed to payment',
		}"
	>
		<template #body-content>
			<div v-if="!props.eventId" class="text-center py-8">
				<p class="text-ink-gray-5">Loading event information...</p>
			</div>

			<div v-else-if="tiers.loading" class="flex justify-center py-8">
				<Spinner />
			</div>

			<div v-else-if="tiers.data && tiers.data.length > 0" class="space-y-4">
				<p class="text-ink-gray-7 mb-6">
					Select a sponsorship tier for
					<strong>{{ eventTitle || "this event" }}</strong> and proceed to payment.
				</p>

				<div class="space-y-3">
					<div
						v-for="tier in tiers.data"
						:key="tier.name"
						class="border border-outline-gray-2 rounded-lg p-4 cursor-pointer transition-all hover:border-outline-gray-3 hover:bg-surface-gray-1"
						:class="{
							'border-outline-gray-4 bg-surface-gray-2':
								selectedTier?.name === tier.name,
						}"
						@click="selectedTier = tier"
					>
						<div class="flex items-center justify-between">
							<div class="flex items-center space-x-3">
								<input
									type="radio"
									:checked="selectedTier?.name === tier.name"
									@change="selectedTier = tier"
									class="text-ink-gray-6"
								/>
								<div>
									<h3 class="font-semibold text-ink-gray-9">{{ tier.title }}</h3>
								</div>
							</div>
							<div class="text-right">
								<p class="font-bold text-lg text-ink-gray-9">
									{{ formatCurrency(tier.price, tier.currency) }}
								</p>
							</div>
						</div>
					</div>
				</div>

				<div
					v-if="selectedTier"
					class="mt-6 p-4 bg-surface-green-1 border border-outline-green-1 rounded-lg"
				>
					<div class="flex items-center justify-between">
						<div>
							<h4 class="font-semibold text-ink-green-2">Selected Tier</h4>
							<p class="text-ink-green-2">{{ selectedTier.title }}</p>
						</div>
						<div class="text-right">
							<p class="text-sm text-ink-green-2">Total Amount</p>
							<p class="font-bold text-xl text-ink-green-2">
								{{ formatCurrency(selectedTier.price, selectedTier.currency) }}
							</p>
						</div>
					</div>
				</div>
			</div>

			<div v-else-if="tiers.error" class="text-center py-8">
				<p class="text-ink-red-2">Error loading sponsorship tiers</p>
				<p class="text-ink-gray-5 text-sm">{{ tiers.error }}</p>
			</div>

			<div v-else class="text-center py-8">
				<p class="text-ink-gray-5">No sponsorship tiers available for this event</p>
			</div>
		</template>

		<template #actions>
			<div class="flex justify-end space-x-3">
				<Button variant="ghost" @click="closeDialog">Cancel</Button>
				<Button
					variant="solid"
					:disabled="!selectedTier || paymentLink.loading"
					:loading="paymentLink.loading"
					@click="proceedToPayment"
				>
					Proceed to Pay
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, watch } from "vue";
import { Dialog, Button, Spinner, createResource, useList } from "frappe-ui";
import { formatCurrency } from "../utils/currency";

const props = defineProps({
	open: {
		type: Boolean,
		default: false,
	},
	enquiryId: {
		type: String,
		required: true,
	},
	eventId: {
		type: String,
		required: true,
	},
	eventTitle: {
		type: String,
		required: false,
	},
});

const emit = defineEmits(["update:open", "payment-started"]);

const isOpen = ref(props.open);
const selectedTier = ref(null);

// Watch for prop changes
watch(
	() => props.open,
	(newVal) => {
		isOpen.value = newVal;
		if (newVal && props.eventId) {
			// Reset selection when dialog opens
			selectedTier.value = null;
			tiers.fetch();
		}
	}
);

watch(isOpen, (newVal) => {
	emit("update:open", newVal);
});

// Resource to fetch sponsorship tiers
const tiers = useList({
	doctype: "Sponsorship Tier",
	filters: { event: props.eventId },
	fields: ["name", "title", "price", "currency"],
	orderBy: "price asc",
	onError: console.error,
	auto: false, // Don't auto-fetch, we'll fetch manually when dialog opens
});

// Resource to create payment link
const paymentLink = createResource({
	url: "buzz.api.create_sponsorship_payment_link",
	onSuccess: (paymentUrl) => {
		emit("payment-started");
		closeDialog();
		// Redirect to payment page
		window.location.href = paymentUrl;
	},
	onError: (error) => {
		console.error("Payment link creation failed:", error);
		// TODO: Show error toast
	},
});

const closeDialog = () => {
	isOpen.value = false;
	selectedTier.value = null;
};

const proceedToPayment = () => {
	if (!selectedTier.value) return;

	paymentLink.submit({
		enquiry_id: props.enquiryId,
		tier_id: selectedTier.value.name,
	});
};
</script>
