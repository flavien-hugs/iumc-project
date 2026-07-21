<script lang="ts">
	import { ArrowsClockwise, File as FileIcon, Trash } from 'phosphor-svelte';
	import type { Component } from 'svelte';

	let {
		id,
		label,
		icon: Icon,
		accept,
		maxSizeMb = 10,
		files = $bindable(null)
	}: {
		id: string;
		label: string;
		icon: Component<{ class?: string }>;
		accept?: string;
		maxSizeMb?: number;
		files?: FileList | null;
	} = $props();

	let inputEl: HTMLInputElement | undefined = $state();
	let error = $state('');
	let previewUrl = $state<string | null>(null);

	const selectedFile = $derived(files?.[0] ?? null);
	const allowedExtensions = $derived(
		(accept ?? '')
			.split(',')
			.map((token) => token.trim().replace(/^\./, '').toLowerCase())
			.filter(Boolean)
	);

	function formatSize(bytes: number): string {
		if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
		if (bytes >= 1024) return `${Math.round(bytes / 1024)} Ko`;
		return `${bytes} octets`;
	}

	function validate(file: File): string {
		const extension = file.name.split('.').pop()?.toLowerCase() ?? '';
		if (allowedExtensions.length > 0 && !allowedExtensions.includes(extension)) {
			return `Format non pris en charge (autorisés : ${allowedExtensions.join(', ')}).`;
		}
		if (file.size > maxSizeMb * 1024 * 1024) {
			return `Fichier trop volumineux (${formatSize(file.size)}), ${maxSizeMb} Mo maximum.`;
		}
		return '';
	}

	function clearPreview() {
		if (previewUrl) URL.revokeObjectURL(previewUrl);
		previewUrl = null;
	}

	function onChange() {
		clearPreview();
		error = '';
		const file = selectedFile;
		if (!file) return;
		const message = validate(file);
		if (message) {
			error = message;
			files = null;
			return;
		}
		if (file.type.startsWith('image/')) {
			previewUrl = URL.createObjectURL(file);
		}
	}

	function remove() {
		files = null;
		error = '';
		clearPreview();
		if (inputEl) inputEl.value = '';
	}

	function replace() {
		inputEl?.click();
	}

	// Un reset externe du `files` bindable (ex. fermeture du tiroir parent) ne
	// passe pas par `remove()` : cet effet rattrape la révocation de l'URL.
	$effect(() => {
		if (!selectedFile && previewUrl) clearPreview();
	});

	$effect(() => clearPreview);
</script>

<div class="flex flex-col gap-2">
	<label for={id} class="text-sm font-medium text-ink-900">{label}</label>

	<input
		bind:this={inputEl}
		{id}
		type="file"
		{accept}
		bind:files
		onchange={onChange}
		class={selectedFile && !error ? 'hidden' : 'sr-only'}
	/>

	{#if selectedFile && !error}
		<div class="flex items-center gap-3 rounded-input border border-ink-900/20 bg-paper-50 p-3">
			{#if previewUrl}
				<img src={previewUrl} alt="" class="h-14 w-14 shrink-0 rounded-input object-cover" />
			{:else}
				<div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-input bg-ink-900/5">
					<FileIcon size={22} class="text-ink-800/50" />
				</div>
			{/if}
			<div class="min-w-0 flex-1">
				<p class="truncate text-sm font-medium text-ink-950" title={selectedFile.name}>
					{selectedFile.name}
				</p>
				<p class="text-xs text-ink-800/60">{formatSize(selectedFile.size)}</p>
			</div>
			<button
				type="button"
				onclick={replace}
				aria-label="Remplacer le fichier"
				class="rounded-input p-2 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
			>
				<ArrowsClockwise size={16} />
			</button>
			<button
				type="button"
				onclick={remove}
				aria-label="Retirer le fichier"
				class="rounded-input p-2 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
			>
				<Trash size={16} />
			</button>
		</div>
	{:else}
		<label for={id} class="relative block cursor-pointer">
			<Icon
				size={18}
				class="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-ink-800/40"
			/>
			<span
				class="flex w-full items-center rounded-input border border-ink-900/20 bg-paper-50 py-2 pr-3 pl-10 text-sm text-ink-800/60"
			>
				Choisir un fichier…
			</span>
		</label>
	{/if}

	{#if error}
		<p class="text-xs text-ink-900" role="alert">{error}</p>
	{/if}
</div>
