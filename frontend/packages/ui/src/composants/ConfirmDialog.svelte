<script lang="ts">
	import { fade, scale } from 'svelte/transition';

	let {
		open = false,
		title,
		description,
		confirmLabel = 'Confirmer',
		cancelLabel = 'Annuler',
		destructive = false,
		requireText,
		loading = false,
		error,
		onconfirm,
		oncancel
	}: {
		open: boolean;
		title: string;
		description?: string;
		confirmLabel?: string;
		cancelLabel?: string;
		destructive?: boolean;
		requireText?: string;
		loading?: boolean;
		error?: string;
		onconfirm: () => void;
		oncancel: () => void;
	} = $props();

	let typedValue = $state('');
	let panelEl: HTMLDivElement | undefined = $state();

	const reduceMotion =
		typeof window !== 'undefined' &&
		window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	const canConfirm = $derived(!requireText || typedValue.trim() === requireText);

	function onKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') oncancel();
	}

	function handleConfirm() {
		if (!canConfirm || loading) return;
		onconfirm();
	}

	$effect(() => {
		if (!open) {
			typedValue = '';
			return;
		}
		const previousOverflow = document.body.style.overflow;
		document.body.style.overflow = 'hidden';
		const id = requestAnimationFrame(() => {
			panelEl?.querySelector<HTMLElement>('input, button')?.focus();
		});
		return () => {
			document.body.style.overflow = previousOverflow;
			cancelAnimationFrame(id);
		};
	});
</script>

<svelte:window onkeydown={open ? onKeydown : undefined} />

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		<button
			type="button"
			aria-label="Fermer"
			onclick={oncancel}
			transition:fade={{ duration: reduceMotion ? 0 : 150 }}
			class="absolute inset-0 bg-ink-950/50"
		></button>

		<div
			bind:this={panelEl}
			transition:scale={{ start: 0.96, duration: reduceMotion ? 0 : 150 }}
			role="alertdialog"
			aria-modal="true"
			aria-label={title}
			class="relative w-full max-w-md rounded-card bg-paper-50 p-6 shadow-2xl"
		>
			<h2 class="text-lg font-semibold text-ink-950">{title}</h2>
			{#if description}
				<p class="mt-2 text-sm text-ink-800/75">{description}</p>
			{/if}

			{#if requireText}
				<div class="mt-4 flex flex-col gap-1.5">
					<label for="confirm-typed-value" class="text-sm font-medium text-ink-900">
						Tapez « {requireText} » pour confirmer
					</label>
					<input
						id="confirm-typed-value"
						type="text"
						bind:value={typedValue}
						autocomplete="off"
						spellcheck="false"
						class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
					/>
				</div>
			{/if}

			{#if error}
				<p class="mt-4 rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
					{error}
				</p>
			{/if}

			<div class="mt-6 flex items-center justify-end gap-3">
				<button
					type="button"
					onclick={oncancel}
					class="rounded-pill border border-ink-900/20 px-4 py-2 text-sm font-medium text-ink-900 hover:border-ink-900/40"
				>
					{cancelLabel}
				</button>
				<button
					type="button"
					onclick={handleConfirm}
					disabled={!canConfirm || loading}
					class={`rounded-pill px-4 py-2 text-sm font-medium disabled:opacity-50 ${
						destructive
							? 'bg-ink-950 text-paper-50 hover:bg-ink-900'
							: 'bg-gold-500 text-ink-950 hover:bg-gold-600'
					}`}
				>
					{loading ? 'Patientez…' : confirmLabel}
				</button>
			</div>
		</div>
	</div>
{/if}
