<script lang="ts">
	import { CaretDown } from 'phosphor-svelte';
	import type { Component } from 'svelte';

	type Option = { value: string; label: string };

	let {
		id,
		label,
		icon: Icon,
		options,
		value = $bindable(''),
		placeholder = 'Rechercher…',
		required = false,
		disabled = false,
		onchange
	}: {
		id: string;
		label: string;
		icon: Component<{ class?: string }>;
		options: Option[];
		value?: string;
		placeholder?: string;
		required?: boolean;
		disabled?: boolean;
		onchange?: (value: string) => void;
	} = $props();

	let query = $state('');
	let open = $state(false);
	let highlighted = $state(-1);
	let inputEl: HTMLInputElement | undefined = $state();
	const listboxId = `${id}-listbox`;

	// Garde l'affichage synchronisé avec la valeur sélectionnée (y compris
	// réinitialisation externe, ex. changement de pôle qui vide le service).
	$effect(() => {
		const match = options.find((o) => o.value === value);
		query = match ? match.label : '';
	});

	$effect(() => {
		inputEl?.setCustomValidity(required && !value ? 'Veuillez choisir une option dans la liste.' : '');
	});

	const filtered = $derived(
		query.trim() === '' || options.some((o) => o.label === query)
			? options
			: options.filter((o) => o.label.toLowerCase().includes(query.toLowerCase()))
	);

	function selectOption(option: Option) {
		value = option.value;
		query = option.label;
		open = false;
		highlighted = -1;
		onchange?.(value);
	}

	function onInput() {
		open = true;
		highlighted = -1;
		if (query === '') {
			value = '';
			onchange?.(value);
		}
	}

	function onKeydown(event: KeyboardEvent) {
		if (!open && (event.key === 'ArrowDown' || event.key === 'Enter')) {
			open = true;
			return;
		}
		if (!open) return;
		if (event.key === 'ArrowDown') {
			event.preventDefault();
			highlighted = Math.min(highlighted + 1, filtered.length - 1);
		} else if (event.key === 'ArrowUp') {
			event.preventDefault();
			highlighted = Math.max(highlighted - 1, 0);
		} else if (event.key === 'Enter') {
			event.preventDefault();
			if (highlighted >= 0 && filtered[highlighted]) selectOption(filtered[highlighted]);
		} else if (event.key === 'Escape') {
			open = false;
			highlighted = -1;
		}
	}

	function onBlur() {
		setTimeout(() => {
			open = false;
			const match = options.find((o) => o.value === value);
			query = match ? match.label : '';
		}, 120);
	}
</script>

<div class="flex flex-col gap-2">
	<label for={id} class="text-sm font-medium text-ink-900">{label}</label>
	<div class="relative">
		<Icon size={18} class="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-ink-800/40" />
		<input
			bind:this={inputEl}
			{id}
			type="text"
			role="combobox"
			aria-expanded={open}
			aria-controls={listboxId}
			aria-autocomplete="list"
			autocomplete="off"
			{disabled}
			placeholder={disabled ? '' : placeholder}
			bind:value={query}
			oninput={onInput}
			onfocus={() => (open = true)}
			onkeydown={onKeydown}
			onblur={onBlur}
			class="w-full rounded-input border border-ink-900/20 bg-paper-50 py-2.5 pr-9 pl-10 text-sm text-ink-950 focus:border-gold-500 focus:ring-1 focus:ring-gold-500 focus:outline-none disabled:opacity-50"
		/>
		<CaretDown
			size={16}
			class="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-ink-800/40"
		/>

		{#if open && !disabled}
			<ul
				id={listboxId}
				role="listbox"
				class="absolute z-10 mt-1 max-h-56 w-full overflow-auto rounded-input border border-ink-900/15 bg-paper-50 py-1 shadow-lg shadow-ink-950/10"
			>
				{#if filtered.length === 0}
					<li class="px-3 py-2 text-sm text-ink-800/50">Aucun résultat</li>
				{/if}
				{#each filtered as option, i (option.value)}
					<li
						role="option"
						aria-selected={option.value === value}
						class={`cursor-pointer px-3 py-2 text-sm ${i === highlighted ? 'bg-ink-900/5 text-ink-950' : 'text-ink-800'} hover:bg-ink-900/5`}
						onmousedown={(event) => event.preventDefault()}
						onclick={() => selectOption(option)}
					>
						{option.label}
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>
