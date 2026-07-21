<script lang="ts">
	import {
		ArrowCounterClockwise,
		EnvelopeSimple,
		IdentificationCard,
		LockKey,
		MapPin,
		Phone,
		Plus,
		Trash,
		UserCircleCheck,
		UserCircleMinus
	} from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { apiCall, ApiError } from '@iumc/api';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import ConfirmDialog from '@iumc/ui/composants/ConfirmDialog.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import SearchSelect from '@iumc/ui/formulaire/SearchSelect.svelte';
	import { formatDateTime, ROLE_LABELS } from '$lib/labels';
	import type { UserRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const usersPage = $derived(data.usersPage);

	const locationOptions = $derived([
		{ value: '', label: 'Aucune implantation' },
		...data.locations.map((location) => ({
			value: String(location.id),
			label: `${location.name} — ${location.city}`
		}))
	]);

	// --- Création ---------------------------------------------------------

	let createOpen = $state(false);
	let name = $state('');
	let email = $state('');
	let password = $state('');
	let role = $state('sales_agent');
	let error = $state('');
	let saving = $state(false);

	function openCreate() {
		name = '';
		email = '';
		password = '';
		role = 'sales_agent';
		error = '';
		createOpen = true;
	}

	async function createUser(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		error = '';
		try {
			await apiCall('/admin/users', { method: 'POST', body: { name, email, password, role } });
			createOpen = false;
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Création impossible.';
		} finally {
			saving = false;
		}
	}

	// --- Détail / édition ---------------------------------------------------

	let editOpen = $state(false);
	let editingUser = $state<UserRow | null>(null);
	let editForm = $state({ name: '', phone: '', role: 'sales_agent', location_id: '' });
	let editSaving = $state(false);
	let editError = $state('');

	function openEdit(user: UserRow) {
		editingUser = user;
		editForm = {
			name: user.name,
			phone: user.phone ?? '',
			role: user.role,
			location_id: user.location_id !== null ? String(user.location_id) : ''
		};
		editError = '';
		editOpen = true;
	}

	async function saveEdit(event: SubmitEvent) {
		event.preventDefault();
		if (!editingUser) return;
		editSaving = true;
		editError = '';
		try {
			await apiCall(`/admin/users/${editingUser.id}`, {
				method: 'PATCH',
				body: {
					name: editForm.name,
					phone: editForm.phone || null,
					role: editForm.role,
					location_id: editForm.location_id ? Number(editForm.location_id) : null
				}
			});
			editOpen = false;
			await invalidateAll();
		} catch (exception) {
			editError = exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			editSaving = false;
		}
	}

	// --- Actions de statut (suspendre/activer/supprimer/restaurer) --------

	type StatusAction = 'suspend' | 'activate' | 'delete' | 'restore';
	let confirmTarget = $state<{ action: StatusAction; user: UserRow } | null>(null);
	let confirmLoading = $state(false);
	let confirmError = $state('');

	function requestStatusAction(user: UserRow, action: StatusAction, event?: MouseEvent) {
		event?.stopPropagation();
		confirmTarget = { action, user };
		confirmError = '';
	}

	function closeConfirm() {
		confirmTarget = null;
		confirmError = '';
	}

	const CONFIRM_COPY: Record<
		StatusAction,
		{ title: string; description: string; confirmLabel: string; destructive: boolean }
	> = {
		suspend: {
			title: 'Suspendre ce compte ?',
			description: "L'utilisateur ne pourra plus se connecter au panel jusqu'à réactivation.",
			confirmLabel: 'Suspendre',
			destructive: false
		},
		activate: {
			title: 'Réactiver ce compte ?',
			description: 'L’utilisateur pourra de nouveau se connecter au panel.',
			confirmLabel: 'Réactiver',
			destructive: false
		},
		delete: {
			title: 'Supprimer ce compte ?',
			description:
				'Le compte sera masqué et ne pourra plus se connecter. Ses données (historique, journaux) sont conservées et une restauration reste possible.',
			confirmLabel: 'Supprimer',
			destructive: true
		},
		restore: {
			title: 'Restaurer ce compte ?',
			description:
				'Le compte redevient visible dans la liste, mais reste suspendu jusqu’à réactivation explicite.',
			confirmLabel: 'Restaurer',
			destructive: false
		}
	};

	async function confirmStatusAction() {
		if (!confirmTarget) return;
		const { action, user } = confirmTarget;
		confirmLoading = true;
		confirmError = '';
		try {
			if (action === 'suspend') {
				await apiCall(`/admin/users/${user.id}`, { method: 'PATCH', body: { is_active: false } });
			} else if (action === 'activate') {
				await apiCall(`/admin/users/${user.id}`, { method: 'PATCH', body: { is_active: true } });
			} else if (action === 'delete') {
				await apiCall(`/admin/users/${user.id}`, { method: 'DELETE' });
			} else {
				await apiCall(`/admin/users/${user.id}/restore`, { method: 'POST' });
			}
			confirmTarget = null;
			await invalidateAll();
		} catch (exception) {
			confirmError =
				exception instanceof ApiError ? exception.message : 'Action impossible.';
		} finally {
			confirmLoading = false;
		}
	}

	function toggleIncludeDeleted() {
		const params = new URLSearchParams(page.url.searchParams);
		if (data.includeDeleted) {
			params.delete('include_deleted');
		} else {
			params.set('include_deleted', 'true');
		}
		params.delete('page');
		goto(`/admin/users${params.size > 0 ? `?${params}` : ''}`, { keepFocus: true });
	}

	function changePage(nextPage: number) {
		const params = new URLSearchParams(page.url.searchParams);
		params.set('page', String(nextPage));
		goto(`/admin/users?${params}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>Utilisateurs, panel IUMC</title>
</svelte:head>

<div class="flex flex-wrap items-center justify-between gap-4">
	<div>
		<h1 class="text-3xl font-semibold text-ink-950">Utilisateurs</h1>
		<p class="mt-2 text-sm text-ink-800/70">Comptes du panel et rôles (PRD section 11.6).</p>
	</div>
	<button
		type="button"
		onclick={openCreate}
		class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
	>
		<Plus size={16} />
		Créer un compte
	</button>
</div>

<label class="mt-4 flex w-fit items-center gap-2 text-sm text-ink-800/70">
	<input
		type="checkbox"
		checked={data.includeDeleted}
		onchange={toggleIncludeDeleted}
		class="accent-gold-500"
	/>
	Afficher les comptes supprimés
</label>

<div class="mt-4 overflow-x-auto rounded-card border border-ink-900/10 bg-paper-50">
	<table class="w-full min-w-160 text-left text-sm">
		<thead>
			<tr class="border-b border-ink-900/10 text-xs tracking-wide text-ink-800/50 uppercase">
				<th class="px-4 py-3 font-medium">#</th>
				<th class="px-4 py-3 font-medium">Nom</th>
				<th class="px-4 py-3 font-medium">Rôle</th>
				<th class="px-4 py-3 font-medium">Dernière connexion</th>
				<th class="px-4 py-3 font-medium">Statut</th>
				<th class="px-4 py-3 font-medium">Actions</th>
			</tr>
		</thead>
		<tbody class="divide-y divide-ink-900/5">
			{#each usersPage.items as user, i (user.id)}
				<tr
					class={user.deleted_at ? '' : 'cursor-pointer hover:bg-ink-900/4'}
					onclick={() => (user.deleted_at ? null : openEdit(user))}
				>
					<td class="px-4 py-3 text-ink-800/50 tabular-nums">
						{(usersPage.page - 1) * usersPage.page_size + i + 1}
					</td>
					<td class="px-4 py-3">
						<span class="block font-medium text-ink-950">{user.name}</span>
						<span class="block text-xs text-ink-800/60">{user.email}</span>
					</td>
					<td class="px-4 py-3 text-ink-800">{ROLE_LABELS[user.role] ?? user.role}</td>
					<td class="px-4 py-3 whitespace-nowrap text-ink-800/70">
						{user.last_login_at ? formatDateTime(user.last_login_at) : 'Jamais'}
					</td>
					<td class="px-4 py-3">
						{#if user.deleted_at}
							<span class="rounded-pill bg-ink-900/5 px-3 py-1 text-xs font-medium text-ink-800/60">
								Supprimé
							</span>
						{:else}
							<span
								class={`rounded-pill px-3 py-1 text-xs font-medium ${
									user.is_active
										? 'bg-gold-500/15 text-gold-600'
										: 'bg-ink-900/5 text-ink-800/60'
								}`}
							>
								{user.is_active ? 'Actif' : 'Suspendu'}
							</span>
						{/if}
					</td>
					<td class="px-4 py-3">
						<div class="flex items-center gap-1">
							{#if user.deleted_at}
								<button
									type="button"
									title="Restaurer"
									aria-label="Restaurer le compte"
									onclick={(event) => requestStatusAction(user, 'restore', event)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
								>
									<ArrowCounterClockwise size={16} />
								</button>
							{:else}
								<button
									type="button"
									title={user.is_active ? 'Suspendre' : 'Réactiver'}
									aria-label={user.is_active ? 'Suspendre le compte' : 'Réactiver le compte'}
									onclick={(event) =>
										requestStatusAction(user, user.is_active ? 'suspend' : 'activate', event)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
								>
									{#if user.is_active}
										<UserCircleMinus size={16} />
									{:else}
										<UserCircleCheck size={16} />
									{/if}
								</button>
								<button
									type="button"
									title="Supprimer"
									aria-label="Supprimer le compte"
									onclick={(event) => requestStatusAction(user, 'delete', event)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
								>
									<Trash size={16} />
								</button>
							{/if}
						</div>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<Pagination
	page={usersPage.page}
	pageSize={usersPage.page_size}
	total={usersPage.total}
	onchange={changePage}
/>

<Drawer open={createOpen} title="Créer un compte" onclose={() => (createOpen = false)}>
	<form class="flex flex-col gap-3" onsubmit={createUser}>
		<TextField id="user-name" label="Nom et prénoms" icon={IdentificationCard} required bind:value={name} />
		<TextField id="user-email" label="Adresse e-mail" type="email" icon={EnvelopeSimple} required bind:value={email} />
		<TextField
			id="user-password"
			label="Mot de passe (10 caractères min.)"
			type="password"
			icon={LockKey}
			required
			minlength={10}
			bind:value={password}
		/>
		<div class="flex flex-col gap-1.5">
			<label for="user-role" class="text-sm font-medium text-ink-900">Rôle</label>
			<select
				id="user-role"
				bind:value={role}
				class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
			>
				{#each Object.entries(ROLE_LABELS) as [value, label] (value)}
					<option {value}>{label}</option>
				{/each}
			</select>
		</div>

		{#if error}
			<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
		{/if}

		<button
			type="submit"
			disabled={saving}
			class="rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
		>
			Créer le compte
		</button>
	</form>
</Drawer>

<Drawer open={editOpen} title="Modifier l'utilisateur" onclose={() => (editOpen = false)}>
	{#if editingUser}
		<form class="flex flex-col gap-3" onsubmit={saveEdit}>
			<TextField id="edit-name" label="Nom et prénoms" icon={IdentificationCard} required bind:value={editForm.name} />
			<div class="flex flex-col gap-1.5">
				<span class="text-sm font-medium text-ink-900">Adresse e-mail</span>
				<div class="flex items-center gap-2 rounded-input border border-ink-900/10 bg-ink-900/4 px-3 py-2 text-sm text-ink-800/70">
					<EnvelopeSimple size={18} class="shrink-0 text-ink-800/40" />
					{editingUser.email}
				</div>
			</div>
			<TextField id="edit-phone" label="Téléphone" icon={Phone} bind:value={editForm.phone} />
			<div class="flex flex-col gap-1.5">
				<label for="edit-role" class="text-sm font-medium text-ink-900">Rôle</label>
				<select
					id="edit-role"
					bind:value={editForm.role}
					class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
				>
					{#each Object.entries(ROLE_LABELS) as [value, label] (value)}
						<option {value}>{label}</option>
					{/each}
				</select>
			</div>
			<SearchSelect
				id="edit-location"
				label="Implantation"
				icon={MapPin}
				options={locationOptions}
				bind:value={editForm.location_id}
			/>

			{#if editError}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
					{editError}
				</p>
			{/if}

			<button
				type="submit"
				disabled={editSaving}
				class="rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
			>
				Enregistrer
			</button>
		</form>
	{/if}
</Drawer>

{#if confirmTarget}
	{@const copy = CONFIRM_COPY[confirmTarget.action]}
	<ConfirmDialog
		open={true}
		title={copy.title}
		description={copy.description}
		confirmLabel={copy.confirmLabel}
		destructive={copy.destructive}
		requireText={confirmTarget.action === 'delete' ? confirmTarget.user.email : undefined}
		loading={confirmLoading}
		error={confirmError}
		onconfirm={confirmStatusAction}
		oncancel={closeConfirm}
	/>
{/if}
