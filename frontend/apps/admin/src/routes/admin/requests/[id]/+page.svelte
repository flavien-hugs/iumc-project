<script lang="ts">
	import {
		CalendarBlank,
		CaretLeft,
		ChatText,
		Clock,
		DownloadSimple,
		FloppyDisk,
		NotePencil
	} from 'phosphor-svelte';
	import { invalidateAll } from '$app/navigation';
	import { apiCall, API_BASE, ApiError } from '@iumc/api';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import TextareaField from '@iumc/ui/formulaire/TextareaField.svelte';
	import {
		APPOINTMENT_STATUS_LABELS,
		CLIENT_TYPE_LABELS,
		CONTACT_PREFERENCE_LABELS,
		formatDate,
		formatDateTime,
		REQUEST_STATUS_CLASSES,
		REQUEST_STATUS_LABELS
	} from '$lib/labels';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const request = $derived(data.request);
	const activeUsers = $derived(data.users.filter((user) => user.is_active));

	let newStatus = $state('');
	let newAgentId = $state('');
	let note = $state('');
	let error = $state('');
	let saving = $state(false);

	let appointmentDate = $state('');
	let appointmentTime = $state('');
	let appointmentNote = $state('');

	async function saveUpdate(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		error = '';
		try {
			await apiCall(`/admin/service-requests/${request.id}`, {
				method: 'PATCH',
				body: {
					status: newStatus || null,
					agent_id: newAgentId ? Number(newAgentId) : null,
					note: note || null
				}
			});
			newStatus = '';
			newAgentId = '';
			note = '';
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			saving = false;
		}
	}

	async function createAppointment(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		error = '';
		try {
			await apiCall(`/admin/service-requests/${request.id}/appointments`, {
				method: 'POST',
				body: {
					date: appointmentDate,
					time: appointmentTime || null,
					note: appointmentNote || null
				}
			});
			appointmentDate = '';
			appointmentTime = '';
			appointmentNote = '';
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Création impossible.';
		} finally {
			saving = false;
		}
	}

	const infoRows = $derived([
		{ label: 'Téléphone', value: request.phone },
		{ label: 'E-mail', value: request.email ?? '-' },
		{ label: 'Entreprise', value: request.company ?? '-' },
		{ label: 'Ville', value: request.city ?? '-' },
		{
			label: 'Type de client',
			value: request.client_type ? (CLIENT_TYPE_LABELS[request.client_type] ?? request.client_type) : '-'
		},
		{
			label: 'Contact préféré',
			value: CONTACT_PREFERENCE_LABELS[request.contact_preference] ?? request.contact_preference
		},
		{
			label: 'RDV souhaité',
			value: request.preferred_appointment_date ? formatDate(request.preferred_appointment_date) : '-'
		},
		{ label: 'Agent affecté', value: request.agent_name ?? 'Non affectée' }
	]);
</script>

<svelte:head>
	<title>{request.reference}, panel IUMC</title>
</svelte:head>

<a
	href="/admin/requests"
	class="inline-flex items-center gap-1 text-sm text-ink-800/70 hover:text-ink-950"
>
	<CaretLeft size={14} />
	Demandes
</a>

<div class="mt-3 flex flex-wrap items-center gap-3">
	<h1 class="text-3xl font-semibold text-ink-950">{request.reference}</h1>
	<span
		class={`rounded-pill px-3 py-1 text-xs font-medium ${REQUEST_STATUS_CLASSES[request.status] ?? 'bg-ink-900/5 text-ink-800'}`}
	>
		{REQUEST_STATUS_LABELS[request.status] ?? request.status}
	</span>
</div>
<p class="mt-1 text-sm text-ink-800/70">
	{request.full_name} · {request.service} ({request.division}) · reçue le
	{formatDate(request.created_at)}
</p>

{#if error}
	<p class="mt-4 rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
		{error}
	</p>
{/if}

<div class="mt-8 grid gap-6 lg:grid-cols-3">
	<div class="space-y-6 lg:col-span-2">
		<section class="rounded-card border border-ink-900/10 bg-paper-50 p-5">
			<h2 class="text-lg font-semibold text-ink-950">Demande</h2>
			{#if request.subject}
				<p class="mt-2 font-medium text-ink-950">{request.subject}</p>
			{/if}
			<p class="mt-2 text-sm whitespace-pre-line text-ink-800/85">{request.description}</p>
			{#if request.attachment}
				<a
					href={`${API_BASE}/admin/service-requests/${request.id}/attachment`}
					class="mt-4 inline-flex items-center gap-2 rounded-pill border border-ink-900/20 px-4 py-2 text-sm font-medium text-ink-900 hover:border-ink-900/40"
				>
					<DownloadSimple size={16} />
					Télécharger la pièce jointe
				</a>
			{/if}
			<dl class="mt-5 grid gap-x-8 gap-y-3 border-t border-ink-900/10 pt-4 sm:grid-cols-2">
				{#each infoRows as row (row.label)}
					<div class="flex justify-between gap-4 text-sm">
						<dt class="text-ink-800/60">{row.label}</dt>
						<dd class="text-right font-medium text-ink-950">{row.value}</dd>
					</div>
				{/each}
			</dl>
		</section>

		<section class="rounded-card border border-ink-900/10 bg-paper-50 p-5">
			<h2 class="text-lg font-semibold text-ink-950">Historique</h2>
			{#if request.history.length === 0}
				<p class="mt-2 text-sm text-ink-800/60">Aucun évènement pour le moment.</p>
			{:else}
				<ol class="mt-4 space-y-4">
					{#each request.history as entry (entry.id)}
						<li class="flex gap-3 text-sm">
							<span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-green-500"></span>
							<div>
								<p class="text-ink-950">
									<span class="font-medium">
										{REQUEST_STATUS_LABELS[entry.new_status] ?? entry.new_status}
									</span>
									{#if entry.previous_status && entry.previous_status !== entry.new_status}
										<span class="text-ink-800/60">
											(depuis {REQUEST_STATUS_LABELS[entry.previous_status] ?? entry.previous_status})
										</span>
									{/if}
								</p>
								{#if entry.note}
									<p class="mt-0.5 text-ink-800/75">{entry.note}</p>
								{/if}
								<p class="mt-0.5 text-xs text-ink-800/50">
									{entry.user_name ?? 'Système'} · {formatDateTime(entry.created_at)}
								</p>
							</div>
						</li>
					{/each}
				</ol>
			{/if}
		</section>
	</div>

	<div class="space-y-6">
		<section class="rounded-card border border-ink-900/10 bg-paper-50 p-5">
			<h2 class="text-lg font-semibold text-ink-950">Traitement</h2>
			<form class="mt-4 flex flex-col gap-4" onsubmit={saveUpdate}>
				<div class="flex flex-col gap-1.5">
					<label for="statut" class="text-sm font-medium text-ink-900">Nouveau statut</label>
					<select
						id="statut"
						bind:value={newStatus}
						class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-green-500 focus:outline-none"
					>
						<option value="">Conserver le statut actuel</option>
						{#each Object.entries(REQUEST_STATUS_LABELS) as [value, label] (value)}
							<option {value}>{label}</option>
						{/each}
					</select>
				</div>

				<div class="flex flex-col gap-1.5">
					<label for="agent" class="text-sm font-medium text-ink-900">Affecter à</label>
					<select
						id="agent"
						bind:value={newAgentId}
						class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-green-500 focus:outline-none"
					>
						<option value="">Conserver l'affectation</option>
						{#each activeUsers as user (user.id)}
							<option value={String(user.id)}>{user.name}</option>
						{/each}
					</select>
				</div>

				<TextareaField id="note" label="Note interne" icon={NotePencil} rows={3} bind:value={note} />

				<button
					type="submit"
					disabled={saving}
					class="inline-flex items-center gap-2 rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600 disabled:opacity-60"
				>
					<FloppyDisk size={16} />
					Enregistrer
				</button>
			</form>
		</section>

		<section class="rounded-card border border-ink-900/10 bg-paper-50 p-5">
			<h2 class="text-lg font-semibold text-ink-950">Rendez-vous</h2>
			{#if request.appointments.length > 0}
				<ul class="mt-3 space-y-2">
					{#each request.appointments as appointment (appointment.id)}
						<li class="rounded-input bg-ink-900/4 px-3 py-2 text-sm">
							<span class="font-medium text-ink-950">
								{formatDate(appointment.date)}{appointment.time ? ` à ${appointment.time.slice(0, 5)}` : ''}
							</span>
							<span class="text-ink-800/60">
								· {APPOINTMENT_STATUS_LABELS[appointment.status] ?? appointment.status}
							</span>
							{#if appointment.note}
								<p class="text-xs text-ink-800/60">{appointment.note}</p>
							{/if}
						</li>
					{/each}
				</ul>
			{/if}
			<form class="mt-4 flex flex-col gap-3" onsubmit={createAppointment}>
				<div class="grid grid-cols-2 gap-3">
					<TextField
						id="rdv-date"
						label="Date"
						type="date"
						icon={CalendarBlank}
						required
						bind:value={appointmentDate}
					/>
					<TextField id="rdv-heure" label="Heure" type="time" icon={Clock} bind:value={appointmentTime} />
				</div>
				<TextField
					id="rdv-note"
					label="Note (facultatif)"
					icon={ChatText}
					placeholder="Précision utile pour ce rendez-vous"
					bind:value={appointmentNote}
				/>
				<button
					type="submit"
					disabled={saving}
					class="inline-flex items-center gap-2 rounded-pill border border-ink-900/20 px-5 py-2 text-sm font-medium text-ink-900 hover:border-ink-900/40 disabled:opacity-60"
				>
					<CalendarBlank size={16} />
					Planifier un rendez-vous
				</button>
			</form>
		</section>
	</div>
</div>
