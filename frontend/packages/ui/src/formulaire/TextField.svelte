<script lang="ts">
	import { Eye, EyeSlash } from 'phosphor-svelte';
	import type { Component } from 'svelte';

	let {
		id,
		label,
		type = 'text',
		icon: Icon,
		value = $bindable(''),
		required = false,
		autocomplete,
		list,
		placeholder,
		minlength,
		compact = false
	}: {
		id: string;
		label: string;
		type?: string;
		icon: Component<{ class?: string }>;
		value?: string;
		required?: boolean;
		autocomplete?: string;
		list?: string;
		placeholder?: string;
		minlength?: number;
		/** Sans label visible (tooltip au survol à la place) — barres d'outils/filtres compacts. */
		compact?: boolean;
	} = $props();

	const isPassword = type === 'password';
	let revealed = $state(false);
	const inputType = $derived(isPassword ? (revealed ? 'text' : 'password') : type);
</script>

<div class={compact ? 'group relative' : 'flex flex-col gap-2'}>
	{#if !compact}
		<label for={id} class="text-sm font-medium text-ink-900">{label}</label>
	{/if}
	<div class="relative">
		<Icon size={18} class="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-ink-800/40" />
		<input
			{id}
			type={inputType}
			{required}
			{autocomplete}
			{list}
			{placeholder}
			{minlength}
			aria-label={compact ? label : undefined}
			bind:value
			class={`w-full rounded-input border border-ink-900/20 bg-paper-50 py-2.5 pl-10 text-sm text-ink-950 focus:border-green-500 focus:ring-1 focus:ring-green-500 focus:outline-none ${isPassword ? 'pr-10' : 'pr-3'}`}
		/>
		{#if isPassword}
			<button
				type="button"
				onclick={() => (revealed = !revealed)}
				aria-label={revealed ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
				aria-pressed={revealed}
				class="absolute top-1/2 right-3 -translate-y-1/2 text-ink-800/40 hover:text-ink-800"
			>
				{#if revealed}
					<EyeSlash size={18} />
				{:else}
					<Eye size={18} />
				{/if}
			</button>
		{/if}
	</div>
	{#if compact}
		<span
			class="pointer-events-none absolute top-full left-0 z-20 mt-2 whitespace-nowrap rounded-input bg-ink-950 px-2.5 py-1.5 text-xs font-medium text-paper-50 opacity-0 shadow-lg transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
		>
			{label}
		</span>
	{/if}
</div>
