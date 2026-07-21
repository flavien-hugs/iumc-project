<script lang="ts">
	import { ArrowClockwise } from 'phosphor-svelte';
	import type { Snippet } from 'svelte';

	let {
		onRefresh,
		refreshing = false,
		filters,
		actions,
		primaryAction
	}: {
		onRefresh?: () => void;
		refreshing?: boolean;
		filters?: Snippet;
		/** Actions secondaires (ex. tri asc/desc) affichées avec les filtres, à gauche. */
		actions?: Snippet;
		/** Action principale de la page (ex. « Nouvel article »), affichée à droite. */
		primaryAction?: Snippet;
	} = $props();
</script>

<div class="mt-6 flex flex-wrap items-end justify-between gap-3">
	<div class="flex flex-wrap items-end gap-3">
		{@render filters?.()}
		{@render actions?.()}
		{#if onRefresh}
			<div class="group relative">
				<button
					type="button"
					onclick={onRefresh}
					disabled={refreshing}
					aria-label="Actualiser"
					class="inline-flex items-center justify-center rounded-pill border border-ink-900/20 p-2.5 text-ink-900 hover:border-ink-900/40 disabled:opacity-60"
				>
					<ArrowClockwise size={16} class={refreshing ? 'animate-spin' : ''} />
				</button>
				<span
					class="pointer-events-none absolute top-full left-0 z-20 mt-2 whitespace-nowrap rounded-input bg-ink-950 px-2.5 py-1.5 text-xs font-medium text-paper-50 opacity-0 shadow-lg transition-opacity group-hover:opacity-100"
				>
					Actualiser
				</span>
			</div>
		{/if}
	</div>
	{#if primaryAction}
		<div class="flex items-center gap-2">
			{@render primaryAction()}
		</div>
	{/if}
</div>
