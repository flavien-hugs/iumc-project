<script lang="ts">
	import { ArrowClockwise } from 'phosphor-svelte';
	import type { Snippet } from 'svelte';

	let {
		onRefresh,
		refreshing = false,
		filters,
		actions
	}: {
		onRefresh?: () => void;
		refreshing?: boolean;
		filters?: Snippet;
		actions?: Snippet;
	} = $props();
</script>

<div class="mt-6 flex flex-wrap items-end justify-between gap-3">
	<div class="flex flex-wrap items-end gap-3">
		{@render filters?.()}
	</div>
	<div class="flex items-center gap-2">
		{@render actions?.()}
		{#if onRefresh}
			<button
				type="button"
				onclick={onRefresh}
				disabled={refreshing}
				class="inline-flex items-center gap-2 rounded-pill border border-ink-900/20 px-4 py-2.5 text-sm font-medium text-ink-900 hover:border-ink-900/40 disabled:opacity-60"
			>
				<ArrowClockwise size={16} class={refreshing ? 'animate-spin' : ''} />
				Actualiser
			</button>
		{/if}
	</div>
</div>
