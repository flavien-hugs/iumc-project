<script lang="ts">
	import { X } from 'phosphor-svelte';
	import { fly } from 'svelte/transition';
	import type { Snippet } from 'svelte';

	let {
		open = false,
		title,
		width = 'md',
		side = 'right',
		onclose,
		children
	}: {
		open: boolean;
		title: string;
		width?: 'sm' | 'md' | 'lg';
		side?: 'left' | 'right';
		onclose: () => void;
		children: Snippet;
	} = $props();

	const WIDTHS = { sm: 'max-w-md', md: 'max-w-xl', lg: 'max-w-3xl' };

	let panelEl: HTMLDivElement | undefined = $state();

	const reduceMotion =
		typeof window !== 'undefined' &&
		window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	const flyParams = { x: side === 'left' ? -40 : 40, duration: reduceMotion ? 0 : 220 };

	function onKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') onclose();
	}

	$effect(() => {
		if (!open) return;
		const previousOverflow = document.body.style.overflow;
		document.body.style.overflow = 'hidden';
		// Focus le premier champ du tiroir pour les utilisateurs clavier.
		const id = requestAnimationFrame(() => {
			panelEl?.querySelector<HTMLElement>('input, textarea, select, button')?.focus();
		});
		return () => {
			document.body.style.overflow = previousOverflow;
			cancelAnimationFrame(id);
		};
	});
</script>

<svelte:window onkeydown={open ? onKeydown : undefined} />

{#if open}
	<div class={`fixed inset-0 z-50 flex ${side === 'left' ? 'justify-start' : 'justify-end'}`}>
		<button
			type="button"
			aria-label="Fermer"
			onclick={onclose}
			class="absolute inset-0 bg-ink-950/40"
		></button>

		<div
			bind:this={panelEl}
			transition:fly={flyParams}
			role="dialog"
			aria-modal="true"
			aria-label={title}
			class={`relative flex h-full w-full ${WIDTHS[width]} flex-col bg-paper-50 shadow-2xl`}
		>
			<div class="flex items-center justify-between border-b border-ink-900/10 px-6 py-4">
				<h2 class="text-lg font-semibold text-ink-950">{title}</h2>
				<button
					type="button"
					onclick={onclose}
					aria-label="Fermer"
					class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
				>
					<X size={18} />
				</button>
			</div>
			<div class="flex-1 overflow-y-auto px-6 py-5">
				{@render children()}
			</div>
		</div>
	</div>
{/if}
