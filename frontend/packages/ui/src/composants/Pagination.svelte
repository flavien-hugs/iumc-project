<script lang="ts">
	import { CaretLeft, CaretRight } from 'phosphor-svelte';

	let {
		page,
		pageSize,
		total,
		onchange
	}: {
		page: number;
		pageSize: number;
		total: number;
		onchange: (page: number) => void;
	} = $props();

	const lastPage = $derived(Math.max(1, Math.ceil(total / pageSize)));
	const rangeStart = $derived(total === 0 ? 0 : (page - 1) * pageSize + 1);
	const rangeEnd = $derived(Math.min(page * pageSize, total));
</script>

{#if total > 0}
	<div class="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-ink-800/70">
		<p>
			{rangeStart}–{rangeEnd} sur {total}
		</p>
		<div class="flex items-center gap-2">
			<button
				type="button"
				disabled={page <= 1}
				onclick={() => onchange(page - 1)}
				aria-label="Page précédente"
				class="flex h-8 w-8 items-center justify-center rounded-input border border-ink-900/15 text-ink-900 hover:border-ink-900/30 disabled:opacity-40"
			>
				<CaretLeft size={14} />
			</button>
			<span class="px-1 tabular-nums">{page} / {lastPage}</span>
			<button
				type="button"
				disabled={page >= lastPage}
				onclick={() => onchange(page + 1)}
				aria-label="Page suivante"
				class="flex h-8 w-8 items-center justify-center rounded-input border border-ink-900/15 text-ink-900 hover:border-ink-900/30 disabled:opacity-40"
			>
				<CaretRight size={14} />
			</button>
		</div>
	</div>
{/if}
