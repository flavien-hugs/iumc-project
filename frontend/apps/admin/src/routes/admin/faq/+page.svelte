<script lang="ts">
	import { Hash, MagnifyingGlass, Plus, Question } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { apiCall, ApiError } from '@iumc/api';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import Toolbar from '@iumc/ui/composants/Toolbar.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import SearchSelect from '@iumc/ui/formulaire/SearchSelect.svelte';
	import RichTextEditor from '@iumc/ui/formulaire/RichTextEditor.svelte';
	import type { FaqRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const faqsPage = $derived(data.faqsPage);

	const publishedOptions = [
		{ value: '', label: 'Tous les statuts' },
		{ value: 'true', label: 'Publiée' },
		{ value: 'false', label: 'Masquée' }
	];

	let searchText = $state(data.q);
	let publishedValue = $state(data.published);
	let refreshing = $state(false);

	function applyFilters(overrides: Record<string, string> = {}) {
		const params = new URLSearchParams();
		const q = overrides.q ?? searchText;
		const published = overrides.published ?? publishedValue;
		if (q.trim()) params.set('q', q.trim());
		if (published) params.set('published', published);
		goto(`/admin/faq${params.size > 0 ? `?${params}` : ''}`, { keepFocus: true });
	}

	function resetFilters() {
		searchText = '';
		publishedValue = '';
		applyFilters({ q: '', published: '' });
	}

	async function refresh() {
		refreshing = true;
		try {
			await invalidateAll();
		} finally {
			refreshing = false;
		}
	}

	const hasActiveFilters = $derived(Boolean(data.q || data.published));

	const EMPTY = { question: '', answer: '', sortOrder: 0 };

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

	function openEdit(faq: FaqRow) {
		editingId = faq.id;
		form = { question: faq.question, answer: faq.answer, sortOrder: faq.sort_order };
		error = '';
		drawerOpen = true;
	}

	async function save(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		error = '';
		const payload = { question: form.question, answer: form.answer, sort_order: form.sortOrder };
		try {
			if (editingId === null) {
				await apiCall('/admin/faqs', { method: 'POST', body: payload });
			} else {
				await apiCall(`/admin/faqs/${editingId}`, { method: 'PATCH', body: payload });
			}
			drawerOpen = false;
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			saving = false;
		}
	}

	async function togglePublished(faq: FaqRow, event: MouseEvent) {
		event.stopPropagation();
		await apiCall(`/admin/faqs/${faq.id}`, { method: 'PATCH', body: { is_published: !faq.is_published } });
		await invalidateAll();
	}

	function changePage(nextPage: number) {
		const params = new URLSearchParams(page.url.searchParams);
		params.set('page', String(nextPage));
		goto(`/admin/faq?${params}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>FAQ, panel IUMC</title>
</svelte:head>

<div class="flex flex-wrap items-center justify-between gap-4">
	<div>
		<h1 class="text-3xl font-semibold text-ink-950">Foire aux questions</h1>
		<p class="mt-2 text-sm text-ink-800/70">Questions affichées sur la page FAQ du site public.</p>
	</div>
	<button
		type="button"
		onclick={openCreate}
		class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
	>
		<Plus size={16} />
		Ajouter une question
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
					placeholder="Question, réponse…"
					bind:value={searchText}
				/>
			</div>
			<div class="w-44">
				<SearchSelect
					id="published-filter"
					label="Statut"
					icon={Question}
					options={publishedOptions}
					bind:value={publishedValue}
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

{#if faqsPage.items.length === 0}
	<div
		class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center"
	>
		<Question size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucune question pour le moment</p>
	</div>
{:else}
	<div class="mt-8 overflow-x-auto rounded-card border border-ink-900/10 bg-paper-50">
		<table class="w-full min-w-140 text-left text-sm">
			<thead>
				<tr class="border-b border-ink-900/10 text-xs tracking-wide text-ink-800/50 uppercase">
					<th class="px-4 py-3 font-medium">#</th>
					<th class="px-4 py-3 font-medium">Question</th>
					<th class="px-4 py-3 font-medium">Ordre</th>
					<th class="px-4 py-3 font-medium">Statut</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-ink-900/5">
				{#each faqsPage.items as faq, i (faq.id)}
					<tr class="cursor-pointer hover:bg-ink-900/4" onclick={() => openEdit(faq)}>
						<td class="px-4 py-3 text-ink-800/50 tabular-nums">
							{(faqsPage.page - 1) * faqsPage.page_size + i + 1}
						</td>
						<td class="max-w-[48ch] px-4 py-3 font-medium text-ink-950">
							<span class="block truncate" title={faq.question}>{faq.question}</span>
						</td>
						<td class="px-4 py-3 text-ink-800 tabular-nums">{faq.sort_order}</td>
						<td class="px-4 py-3">
							<button
								type="button"
								onclick={(event) => togglePublished(faq, event)}
								class={`rounded-pill px-3 py-1 text-xs font-medium ${faq.is_published ? 'bg-gold-500/15 text-gold-600 hover:bg-gold-500/25' : 'bg-ink-900/5 text-ink-800/60 hover:bg-ink-900/10'}`}
							>
								{faq.is_published ? 'Publiée' : 'Masquée'}
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<Pagination
		page={faqsPage.page}
		pageSize={faqsPage.page_size}
		total={faqsPage.total}
		onchange={changePage}
	/>
{/if}

<Drawer
	open={drawerOpen}
	title={editingId === null ? 'Ajouter une question' : 'Modifier la question'}
	onclose={() => (drawerOpen = false)}
>
	<form class="flex flex-col gap-3" onsubmit={save}>
		<TextField id="faq-question" label="Question" icon={Question} required bind:value={form.question} />
		<RichTextEditor id="faq-answer" label="Réponse" bind:value={form.answer} placeholder="Réponse affichée sur la page FAQ…" />
		<div class="flex flex-col gap-1.5">
			<label for="faq-order" class="text-sm font-medium text-ink-900">Ordre d'affichage</label>
			<div class="relative w-24">
				<Hash size={16} class="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-ink-800/40" />
				<input
					id="faq-order"
					type="number"
					bind:value={form.sortOrder}
					class="w-full rounded-input border border-ink-900/20 bg-paper-50 py-2 pr-2 pl-9 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
				/>
			</div>
		</div>

		{#if error}
			<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
		{/if}

		<button
			type="submit"
			disabled={saving}
			class="rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
		>
			{editingId === null ? 'Ajouter' : 'Enregistrer'}
		</button>
	</form>
</Drawer>
