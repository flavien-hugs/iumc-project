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
		minlength
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
	} = $props();

	const isPassword = type === 'password';
	let revealed = $state(false);
	const inputType = $derived(isPassword ? (revealed ? 'text' : 'password') : type);
</script>

<div class="flex flex-col gap-2">
	<label for={id} class="text-sm font-medium text-ink-900">{label}</label>
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
			bind:value
			class={`w-full rounded-input border border-ink-900/20 bg-paper-50 py-2.5 pl-10 text-sm text-ink-950 focus:border-gold-500 focus:ring-1 focus:ring-gold-500 focus:outline-none ${isPassword ? 'pr-10' : 'pr-3'}`}
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
</div>
