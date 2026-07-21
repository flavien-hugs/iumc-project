<script lang="ts">
	import type { Component } from 'svelte';

	let {
		id,
		label,
		icon: Icon,
		value = $bindable(''),
		required = false,
		rows = 4
	}: {
		id: string;
		label: string;
		icon: Component<{ class?: string }>;
		value?: string;
		required?: boolean;
		rows?: number;
	} = $props();
</script>

<div class="flex flex-col gap-2">
	<label for={id} class="text-sm font-medium text-ink-900">{label}</label>
	<div class="relative">
		<Icon size={18} class="pointer-events-none absolute top-3 left-3 text-ink-800/40" />
		<textarea
			{id}
			{rows}
			{required}
			bind:value
			class="w-full rounded-input border border-ink-900/20 bg-paper-50 py-2.5 pr-3 pl-10 text-sm text-ink-950 focus:border-gold-500 focus:ring-1 focus:ring-gold-500 focus:outline-none"
		></textarea>
	</div>
</div>
