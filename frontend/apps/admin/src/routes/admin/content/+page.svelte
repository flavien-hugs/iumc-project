<script lang="ts">
	import {
		ArrowCounterClockwise,
		CheckCircle,
		FloppyDisk,
		PencilSimple,
		Plus,
		Trash,
		X,
		XCircle
	} from 'phosphor-svelte';
	import { invalidateAll } from '$app/navigation';
	import { apiCall, ApiError } from '@iumc/api';
	import ConfirmDialog from '@iumc/ui/composants/ConfirmDialog.svelte';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import Tabs from '@iumc/ui/composants/Tabs.svelte';
	import SearchSelect from '@iumc/ui/formulaire/SearchSelect.svelte';
	import type { ServiceRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const DIVISION_STATUS_LABELS: Record<string, string> = {
		active: 'Actif',
		coming_soon: 'Bientôt disponible',
		inactive: 'Inactif',
		hidden: 'Masqué'
	};

	const divisionStatusOptions = Object.entries(DIVISION_STATUS_LABELS).map(([value, label]) => ({
		value,
		label
	}));

	const tabs = $derived(
		data.divisions.map((division) => ({ id: division.slug, label: division.name }))
	);
	let activeTab = $state(data.divisions[0]?.slug ?? '');
	const activeDivision = $derived(
		data.divisions.find((division) => division.slug === activeTab) ?? data.divisions[0]
	);

	// Pagination client : la liste complète est déjà chargée avec les pôles,
	// on découpe seulement l'affichage (au-delà de 10 services).
	const SERVICES_PAGE_SIZE = 10;
	let servicesPage = $state(1);
	const servicesTotal = $derived(activeDivision?.services.length ?? 0);
	// Clampe au lieu de réinitialiser au changement d'onglet : une page hors
	// bornes (onglet plus court) retombe sur la dernière page valide.
	const currentServicesPage = $derived(
		Math.min(servicesPage, Math.max(1, Math.ceil(servicesTotal / SERVICES_PAGE_SIZE)))
	);
	const visibleServices = $derived(
		(activeDivision?.services ?? []).slice(
			(currentServicesPage - 1) * SERVICES_PAGE_SIZE,
			currentServicesPage * SERVICES_PAGE_SIZE
		)
	);

	async function setDivisionStatus(id: number, status: string) {
		await apiCall(`/admin/divisions/${id}`, { method: 'PATCH', body: { status } });
		await invalidateAll();
	}

	async function toggleService(id: number, status: string) {
		await apiCall(`/admin/services/${id}`, {
			method: 'PATCH',
			body: { status: status === 'active' ? 'inactive' : 'active' }
		});
		await invalidateAll();
	}

	function focusOnMount(node: HTMLInputElement) {
		node.focus();
		node.select();
	}

	let editingServiceId = $state<number | null>(null);
	let editingTitle = $state('');
	let savingService = $state(false);

	function startEdit(service: ServiceRow) {
		editingServiceId = service.id;
		editingTitle = service.title;
	}

	function cancelEdit() {
		editingServiceId = null;
		editingTitle = '';
	}

	async function saveEdit(service: ServiceRow) {
		const title = editingTitle.trim();
		if (!title || title === service.title) {
			cancelEdit();
			return;
		}
		savingService = true;
		try {
			await apiCall(`/admin/services/${service.id}`, { method: 'PATCH', body: { title } });
			await invalidateAll();
			cancelEdit();
		} finally {
			savingService = false;
		}
	}

	async function restoreService(service: ServiceRow) {
		await apiCall(`/admin/services/${service.id}/restore`, { method: 'POST' });
		await invalidateAll();
	}

	let deleteTarget = $state<ServiceRow | null>(null);
	let deleting = $state(false);
	let deleteError = $state('');

	function requestDelete(service: ServiceRow) {
		deleteTarget = service;
		deleteError = '';
	}

	async function confirmDelete() {
		if (!deleteTarget) return;
		deleting = true;
		deleteError = '';
		try {
			await apiCall(`/admin/services/${deleteTarget.id}`, { method: 'DELETE' });
			deleteTarget = null;
			await invalidateAll();
		} catch (exception) {
			deleteError = exception instanceof ApiError ? exception.message : 'Suppression impossible.';
		} finally {
			deleting = false;
		}
	}

	let creatingDivisionId = $state<number | null>(null);
	let newServiceTitle = $state('');
	let creatingSaving = $state(false);

	function startCreate(divisionId: number) {
		creatingDivisionId = divisionId;
		newServiceTitle = '';
	}

	function cancelCreate() {
		creatingDivisionId = null;
		newServiceTitle = '';
	}

	async function saveCreate(divisionId: number) {
		const title = newServiceTitle.trim();
		if (!title) return;
		creatingSaving = true;
		try {
			await apiCall('/admin/services', {
				method: 'POST',
				body: { division_id: divisionId, title }
			});
			await invalidateAll();
			cancelCreate();
		} finally {
			creatingSaving = false;
		}
	}
</script>

<svelte:head>
	<title>Pôles et services, panel IUMC</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-ink-950">Pôles & services</h1>
<p class="mt-2 text-sm text-ink-800/70">
	Activez, masquez ou désactivez les pôles et services affichés sur le site public. L'édition
	des contenus détaillés arrivera avec le module complet.
</p>

<div class="mt-6">
	<Tabs {tabs} bind:active={activeTab} />
</div>

{#if activeDivision}
	<section class="mt-6 rounded-card border border-ink-900/10 bg-paper-50 p-5">
		<div class="flex flex-wrap items-center justify-between gap-3">
			<h2 class="text-lg font-semibold text-ink-950">{activeDivision.name}</h2>
			<div class="w-44">
				<SearchSelect
					id={`division-status-${activeDivision.id}`}
					label={`Statut du pôle ${activeDivision.name}`}
					icon={CheckCircle}
					options={divisionStatusOptions}
					value={activeDivision.status}
					onchange={(value) => setDivisionStatus(activeDivision.id, value)}
					compact
				/>
			</div>
		</div>
		{#if activeDivision.services.length === 0 && creatingDivisionId !== activeDivision.id}
			<p class="mt-3 text-sm text-ink-800/60">Aucun service pour ce pôle.</p>
		{:else}
			<ul class="mt-4 divide-y divide-ink-900/5">
				{#each visibleServices as service, i (service.id)}
					{@const number = (currentServicesPage - 1) * SERVICES_PAGE_SIZE + i + 1}
					<li class="flex items-center justify-between gap-4 py-2.5 text-sm">
						{#if editingServiceId === service.id}
							<span class="flex flex-1 items-baseline gap-3">
								<span class="text-ink-800/50 tabular-nums">{number}.</span>
								<input
									type="text"
									bind:value={editingTitle}
									disabled={savingService}
									use:focusOnMount
									onkeydown={(event) => {
										if (event.key === 'Enter') saveEdit(service);
										if (event.key === 'Escape') cancelEdit();
									}}
									class="w-full max-w-md rounded-input border border-ink-900/20 bg-paper-50 px-2.5 py-1 text-sm text-ink-950 focus:border-green-500 focus:outline-none"
								/>
							</span>
							<div class="flex items-center gap-1">
								<button
									type="button"
									title="Enregistrer"
									aria-label="Enregistrer le titre"
									disabled={savingService}
									onclick={() => saveEdit(service)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950 disabled:opacity-60"
								>
									<FloppyDisk size={16} />
								</button>
								<button
									type="button"
									title="Annuler"
									aria-label="Annuler la modification"
									disabled={savingService}
									onclick={cancelEdit}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950 disabled:opacity-60"
								>
									<X size={16} />
								</button>
							</div>
						{:else if service.deleted_at}
							<span class="flex items-baseline gap-3">
								<span class="text-ink-800/50 tabular-nums">{number}.</span>
								<span class="text-ink-800/50 line-through">{service.title}</span>
								<span
									class="rounded-pill bg-ink-900/5 px-2.5 py-0.5 text-xs font-medium whitespace-nowrap text-ink-800/60"
								>
									Retiré
								</span>
							</span>
							<button
								type="button"
								title="Restaurer"
								aria-label="Restaurer le service"
								onclick={() => restoreService(service)}
								class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
							>
								<ArrowCounterClockwise size={16} />
							</button>
						{:else}
							<span class="flex items-baseline gap-3">
								<span class="text-ink-800/50 tabular-nums">{number}.</span>
								<span class={service.status === 'active' ? 'text-ink-950' : 'text-ink-800/50 line-through'}>
									{service.title}
								</span>
							</span>
							<div class="flex items-center gap-1">
								<button
									type="button"
									title="Modifier"
									aria-label="Modifier le titre"
									onclick={() => startEdit(service)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
								>
									<PencilSimple size={16} />
								</button>
								<button
									type="button"
									onclick={() => toggleService(service.id, service.status)}
									class={`inline-flex items-center gap-1.5 rounded-pill px-3 py-1 text-xs font-medium whitespace-nowrap ${
										service.status === 'active'
											? 'bg-green-500/15 text-green-600 hover:bg-green-500/25'
											: 'bg-ink-900/5 text-ink-800/60 hover:bg-ink-900/10'
									}`}
								>
									{#if service.status === 'active'}
										<CheckCircle size={14} />
									{:else}
										<XCircle size={14} />
									{/if}
									{service.status === 'active' ? 'Actif' : 'Inactif'}
								</button>
								<button
									type="button"
									title="Retirer"
									aria-label="Retirer le service"
									onclick={() => requestDelete(service)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
								>
									<Trash size={16} />
								</button>
							</div>
						{/if}
					</li>
				{/each}
					{#if creatingDivisionId === activeDivision.id}
						<li class="flex items-center justify-between gap-4 py-2.5 text-sm">
							<span class="flex flex-1 items-baseline gap-3">
								<span class="text-ink-800/50 tabular-nums">{servicesTotal + 1}.</span>
								<input
									type="text"
									placeholder="Titre du service"
									bind:value={newServiceTitle}
									disabled={creatingSaving}
									use:focusOnMount
									onkeydown={(event) => {
										if (event.key === 'Enter') saveCreate(activeDivision.id);
										if (event.key === 'Escape') cancelCreate();
									}}
									class="w-full max-w-md rounded-input border border-ink-900/20 bg-paper-50 px-2.5 py-1 text-sm text-ink-950 focus:border-green-500 focus:outline-none"
								/>
							</span>
							<div class="flex items-center gap-1">
								<button
									type="button"
									title="Ajouter"
									aria-label="Ajouter le service"
									disabled={creatingSaving}
									onclick={() => saveCreate(activeDivision.id)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950 disabled:opacity-60"
								>
									<FloppyDisk size={16} />
								</button>
								<button
									type="button"
									title="Annuler"
									aria-label="Annuler l'ajout"
									disabled={creatingSaving}
									onclick={cancelCreate}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950 disabled:opacity-60"
								>
									<X size={16} />
								</button>
							</div>
						</li>
					{/if}
			</ul>
			{#if servicesTotal > SERVICES_PAGE_SIZE}
				<Pagination
					page={currentServicesPage}
					pageSize={SERVICES_PAGE_SIZE}
					total={servicesTotal}
					onchange={(next) => (servicesPage = next)}
				/>
			{/if}
		{/if}
		{#if creatingDivisionId !== activeDivision.id}
			<button
				type="button"
				onclick={() => startCreate(activeDivision.id)}
				class="mt-3 inline-flex items-center gap-2 text-sm font-medium text-green-600 hover:text-green-700"
			>
				<Plus size={16} />
				Ajouter un service
			</button>
		{/if}
	</section>
{/if}

{#if deleteTarget}
	<ConfirmDialog
		open={true}
		title="Retirer ce service ?"
		description={`« ${deleteTarget.title} » sera masqué du site public et de cette liste. Vous pourrez le restaurer à tout moment.`}
		confirmLabel="Retirer"
		destructive
		loading={deleting}
		error={deleteError}
		onconfirm={confirmDelete}
		oncancel={() => (deleteTarget = null)}
	/>
{/if}
