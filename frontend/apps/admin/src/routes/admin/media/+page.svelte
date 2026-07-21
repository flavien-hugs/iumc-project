<script lang="ts">
	import { Images, Plus, UploadSimple } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { apiCall, API_BASE, ApiError } from '@iumc/api';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import ConfirmDialog from '@iumc/ui/composants/ConfirmDialog.svelte';
	import FileField from '@iumc/ui/formulaire/FileField.svelte';
	import { formatDate } from '$lib/labels';
	import type { MediaRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const mediaPage = $derived(data.mediaPage);

	let drawerOpen = $state(false);
	let files = $state<FileList | null>(null);
	let uploading = $state(false);
	let error = $state('');

	function formatSize(bytes: number): string {
		if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
		if (bytes >= 1024) return `${Math.round(bytes / 1024)} Ko`;
		return `${bytes} octets`;
	}

	async function upload(event: SubmitEvent) {
		event.preventDefault();
		const file = files?.[0];
		if (!file) return;
		uploading = true;
		error = '';
		try {
			const form = new FormData();
			form.append('file', file);
			const response = await fetch(`${API_BASE}/admin/media`, {
				method: 'POST',
				credentials: 'include',
				body: form
			});
			if (!response.ok) {
				const detail = await response.json().catch(() => ({}));
				throw new ApiError(response.status, detail.detail ?? 'Téléversement impossible.');
			}
			files = null;
			drawerOpen = false;
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Téléversement impossible.';
		} finally {
			uploading = false;
		}
	}

	let deleteTarget = $state<MediaRow | null>(null);
	let deleteLoading = $state(false);
	let deleteError = $state('');

	async function confirmRemove() {
		if (!deleteTarget) return;
		deleteLoading = true;
		deleteError = '';
		try {
			await apiCall(`/admin/media/${deleteTarget.id}`, { method: 'DELETE' });
			deleteTarget = null;
			await invalidateAll();
		} catch (exception) {
			deleteError = exception instanceof ApiError ? exception.message : 'Suppression impossible.';
		} finally {
			deleteLoading = false;
		}
	}

	function changePage(nextPage: number) {
		goto(`/admin/media?page=${nextPage}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>Médias, panel IUMC</title>
</svelte:head>

<div class="flex flex-wrap items-center justify-between gap-4">
	<div>
		<h1 class="text-3xl font-semibold text-ink-950">Médiathèque</h1>
		<p class="mt-2 text-sm text-ink-800/70">
			Images et documents réutilisables (JPG, PNG, WebP, SVG, PDF, 10 Mo max).
		</p>
	</div>
	<button
		type="button"
		onclick={() => {
			files = null;
			error = '';
			drawerOpen = true;
		}}
		class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
	>
		<Plus size={16} />
		Ajouter un média
	</button>
</div>

{#if mediaPage.items.length === 0}
	<div
		class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center"
	>
		<Images size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucun fichier pour le moment</p>
	</div>
{:else}
	<div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each mediaPage.items as item (item.id)}
			<article class="overflow-hidden rounded-card border border-ink-900/10 bg-paper-50">
				{#if item.mime_type.startsWith('image/')}
					<img
						src={`${API_BASE}/media/${item.id}/file`}
						alt={item.name}
						loading="lazy"
						class="h-36 w-full bg-ink-900/5 object-cover"
					/>
				{:else}
					<div
						class="flex h-36 items-center justify-center bg-ink-900/5 text-xs font-medium tracking-wide text-ink-800/50 uppercase"
					>
						{item.mime_type.split('/')[1]}
					</div>
				{/if}
				<div class="p-3">
					<p class="truncate text-sm font-medium text-ink-950" title={item.name}>{item.name}</p>
					<p class="mt-0.5 text-xs text-ink-800/60">
						{formatSize(item.size)} · {formatDate(item.created_at)}
					</p>
					<div class="mt-2 flex gap-2">
						<a
							href={`${API_BASE}/media/${item.id}/file`}
							target="_blank"
							rel="noopener noreferrer"
							class="rounded-pill border border-ink-900/20 px-3 py-1 text-xs font-medium text-ink-900 hover:border-ink-900/40"
						>
							Ouvrir
						</a>
						<button
							type="button"
							onclick={() => (deleteTarget = item)}
							class="rounded-pill border border-ink-900/20 px-3 py-1 text-xs font-medium text-ink-800/70 hover:border-ink-900/40"
						>
							Supprimer
						</button>
					</div>
				</div>
			</article>
		{/each}
	</div>

	<Pagination
		page={mediaPage.page}
		pageSize={mediaPage.page_size}
		total={mediaPage.total}
		onchange={changePage}
	/>
{/if}

<Drawer open={drawerOpen} title="Ajouter un média" onclose={() => (drawerOpen = false)}>
	<form class="flex flex-col gap-4" onsubmit={upload}>
		<FileField
			id="media-file"
			label="Fichier"
			icon={UploadSimple}
			accept=".jpg,.jpeg,.png,.webp,.svg,.pdf"
			maxSizeMb={10}
			bind:files
		/>

		{#if error}
			<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
		{/if}

		<button
			type="submit"
			disabled={uploading || !files?.length}
			class="inline-flex items-center justify-center gap-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
		>
			<UploadSimple size={16} />
			{uploading ? 'Téléversement…' : 'Téléverser'}
		</button>
	</form>
</Drawer>

<ConfirmDialog
	open={deleteTarget !== null}
	title="Supprimer ce média ?"
	description={deleteTarget
		? `« ${deleteTarget.name} » sera définitivement supprimé. S'il est utilisé sur le site public, l'image cessera de s'afficher.`
		: ''}
	confirmLabel="Supprimer"
	destructive
	loading={deleteLoading}
	error={deleteError}
	onconfirm={confirmRemove}
	oncancel={() => (deleteTarget = null)}
/>
