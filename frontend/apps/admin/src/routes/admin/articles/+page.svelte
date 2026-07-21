<script lang="ts">
	import { Article as ArticleIcon, MagnifyingGlass, Plus, Tag, TextAa, User } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { apiCall, ApiError } from '@iumc/api';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import Toolbar from '@iumc/ui/composants/Toolbar.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import SearchSelect from '@iumc/ui/formulaire/SearchSelect.svelte';
	import RichTextEditor from '@iumc/ui/formulaire/RichTextEditor.svelte';
	import { formatDate } from '$lib/labels';
	import type { ArticleRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const articlesPage = $derived(data.articlesPage);

	const STATUS_LABELS: Record<string, string> = {
		draft: 'Brouillon',
		scheduled: 'Programmé',
		published: 'Publié',
		archived: 'Archivé'
	};

	const statusOptions = [
		{ value: '', label: 'Tous les statuts' },
		...Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }))
	];
	const authorOptions = $derived([
		{ value: '', label: 'Tous les auteurs' },
		...data.authors.map((author) => ({ value: String(author.id), label: author.name }))
	]);

	let searchText = $state(data.q);
	let statusValue = $state(data.status);
	let categoryValue = $state(data.category);
	let authorValue = $state(data.authorId);
	let refreshing = $state(false);

	function applyFilters(overrides: Record<string, string> = {}) {
		const params = new URLSearchParams();
		const q = overrides.q ?? searchText;
		const status = overrides.status ?? statusValue;
		const category = overrides.category ?? categoryValue;
		const authorId = overrides.authorId ?? authorValue;
		if (q.trim()) params.set('q', q.trim());
		if (status) params.set('status', status);
		if (category.trim()) params.set('category', category.trim());
		if (authorId) params.set('author_id', authorId);
		goto(`/admin/articles${params.size > 0 ? `?${params}` : ''}`, { keepFocus: true });
	}

	function resetFilters() {
		searchText = '';
		statusValue = '';
		categoryValue = '';
		authorValue = '';
		applyFilters({ q: '', status: '', category: '', authorId: '' });
	}

	async function refresh() {
		refreshing = true;
		try {
			await invalidateAll();
		} finally {
			refreshing = false;
		}
	}

	const hasActiveFilters = $derived(
		Boolean(data.q || data.status || data.category || data.authorId)
	);

	const EMPTY = { title: '', category: '', summary: '', body: '', status: 'draft' };

	let drawerOpen = $state(false);
	let editingId = $state<number | null>(null);
	let form = $state({ ...EMPTY });
	let saving = $state(false);
	let error = $state('');

	function openCreate() {
		editingId = null;
		form = { ...EMPTY };
		error = '';
		drawerOpen = true;
	}

	function openEdit(article: ArticleRow) {
		editingId = article.id;
		form = {
			title: article.title,
			category: article.category ?? '',
			summary: article.summary ?? '',
			body: article.body ?? '',
			status: article.status
		};
		error = '';
		drawerOpen = true;
	}

	async function save(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		error = '';
		const payload = {
			title: form.title,
			category: form.category || null,
			summary: form.summary || null,
			body: form.body || null,
			status: form.status
		};
		try {
			if (editingId === null) {
				await apiCall('/admin/articles', { method: 'POST', body: payload });
			} else {
				await apiCall(`/admin/articles/${editingId}`, { method: 'PATCH', body: payload });
			}
			drawerOpen = false;
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			saving = false;
		}
	}

	function changePage(nextPage: number) {
		const params = new URLSearchParams(page.url.searchParams);
		params.set('page', String(nextPage));
		goto(`/admin/articles?${params}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>Articles, panel IUMC</title>
</svelte:head>

<div class="flex flex-wrap items-center justify-between gap-4">
	<div>
		<h1 class="text-3xl font-semibold text-ink-950">Articles</h1>
		<p class="mt-2 text-sm text-ink-800/70">Actualités et conseils publiés sur le site.</p>
	</div>
	<button
		type="button"
		onclick={openCreate}
		class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
	>
		<Plus size={16} />
		Nouvel article
	</button>
</div>

<Toolbar onRefresh={refresh} {refreshing}>
	{#snippet filters()}
		<form
			class="flex flex-wrap items-end gap-3"
			onsubmit={(event) => {
				event.preventDefault();
				applyFilters();
			}}
		>
			<div class="w-56">
				<TextField
					id="q"
					label="Recherche"
					icon={MagnifyingGlass}
					placeholder="Titre, résumé…"
					bind:value={searchText}
				/>
			</div>
			<div class="w-44">
				<SearchSelect
					id="status-filter"
					label="Statut"
					icon={Tag}
					options={statusOptions}
					bind:value={statusValue}
					onchange={() => applyFilters()}
				/>
			</div>
			<div class="w-48">
				<TextField
					id="category-filter"
					label="Catégorie"
					icon={Tag}
					placeholder="Conseil foncier…"
					bind:value={categoryValue}
				/>
			</div>
			<div class="w-52">
				<SearchSelect
					id="author-filter"
					label="Auteur"
					icon={User}
					options={authorOptions}
					bind:value={authorValue}
					onchange={() => applyFilters()}
				/>
			</div>
			<button
				type="submit"
				class="rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
			>
				Filtrer
			</button>
			{#if hasActiveFilters}
				<button
					type="button"
					onclick={resetFilters}
					class="rounded-pill border border-ink-900/20 px-4 py-2.5 text-sm font-medium text-ink-900 hover:border-ink-900/40"
				>
					Réinitialiser
				</button>
			{/if}
		</form>
	{/snippet}
</Toolbar>

{#if articlesPage.items.length === 0}
	<div
		class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center"
	>
		<ArticleIcon size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucun article pour le moment</p>
	</div>
{:else}
	<div class="mt-8 overflow-x-auto rounded-card border border-ink-900/10 bg-paper-50">
		<table class="w-full min-w-140 text-left text-sm">
			<thead>
				<tr class="border-b border-ink-900/10 text-xs tracking-wide text-ink-800/50 uppercase">
					<th class="px-4 py-3 font-medium">#</th>
					<th class="px-4 py-3 font-medium">Titre</th>
					<th class="px-4 py-3 font-medium">Catégorie</th>
					<th class="px-4 py-3 font-medium">Auteur</th>
					<th class="px-4 py-3 font-medium">Statut</th>
					<th class="px-4 py-3 font-medium">Publié le</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-ink-900/5">
				{#each articlesPage.items as article, i (article.id)}
					<tr class="cursor-pointer hover:bg-ink-900/4" onclick={() => openEdit(article)}>
						<td class="px-4 py-3 text-ink-800/50 tabular-nums">
							{(articlesPage.page - 1) * articlesPage.page_size + i + 1}
						</td>
						<td class="px-4 py-3 font-medium text-ink-950">{article.title}</td>
						<td class="px-4 py-3 text-ink-800">{article.category ?? '-'}</td>
						<td class="px-4 py-3 text-ink-800">{article.author_name ?? '-'}</td>
						<td class="px-4 py-3">
							<span
								class={`rounded-pill px-2.5 py-1 text-xs font-medium ${article.status === 'published' ? 'bg-gold-500/15 text-gold-600' : 'bg-ink-900/5 text-ink-800/70'}`}
							>
								{STATUS_LABELS[article.status] ?? article.status}
							</span>
						</td>
						<td class="px-4 py-3 whitespace-nowrap text-ink-800/70">
							{article.published_at ? formatDate(article.published_at) : '-'}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<Pagination
		page={articlesPage.page}
		pageSize={articlesPage.page_size}
		total={articlesPage.total}
		onchange={changePage}
	/>
{/if}

<Drawer
	open={drawerOpen}
	title={editingId === null ? 'Nouvel article' : "Modifier l'article"}
	onclose={() => (drawerOpen = false)}
	width="lg"
>
	<form class="flex flex-col gap-4" onsubmit={save}>
		<TextField id="titre" label="Titre" icon={TextAa} required bind:value={form.title} />
		<div class="grid gap-4 sm:grid-cols-2">
			<TextField
				id="categorie"
				label="Catégorie"
				icon={Tag}
				placeholder="Conseil foncier, Annonce…"
				bind:value={form.category}
			/>
			<div class="flex flex-col gap-1.5">
				<label for="statut" class="text-sm font-medium text-ink-900">Statut</label>
				<select
					id="statut"
					bind:value={form.status}
					class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
				>
					{#each Object.entries(STATUS_LABELS) as [value, label] (value)}
						<option {value}>{label}</option>
					{/each}
				</select>
			</div>
		</div>
		<RichTextEditor id="resume" label="Résumé" bind:value={form.summary} placeholder="Résumé affiché dans les listes d'articles…" />
		<RichTextEditor id="contenu" label="Contenu" bind:value={form.body} placeholder="Contenu de l'article…" />

		{#if error}
			<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
		{/if}

		<button
			type="submit"
			disabled={saving}
			class="rounded-pill bg-gold-500 px-6 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
		>
			{editingId === null ? "Créer l'article" : 'Enregistrer'}
		</button>
	</form>
</Drawer>
