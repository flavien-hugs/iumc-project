<script lang="ts">
	import {
		Buildings,
		CalendarBlank,
		Clock,
		EnvelopeSimple,
		FacebookLogo,
		FloppyDisk,
		LinkedinLogo,
		MapPin,
		Phone,
		Plus,
		Scales,
		Star,
		Trash,
		WhatsappLogo,
		XLogo,
		YoutubeLogo
	} from 'phosphor-svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { apiCall, ApiError } from '@iumc/api';
	import Tabs from '@iumc/ui/composants/Tabs.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import RichTextEditor from '@iumc/ui/formulaire/RichTextEditor.svelte';
	import type { CompanyAbout } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const FIELD_LABELS: Record<string, string> = {
		company_phone: 'Téléphone principal',
		company_whatsapp: 'Numéro WhatsApp',
		company_email: 'Adresse e-mail',
		company_address: 'Adresse du siège',
		opening_hours: "Horaires d'ouverture",
		facebook_url: 'Page Facebook',
		linkedin_url: 'Page LinkedIn',
		x_url: 'Compte X',
		youtube_url: 'Chaîne YouTube'
	};

	const FIELD_ICONS: Record<string, typeof Phone> = {
		company_phone: Phone,
		company_whatsapp: WhatsappLogo,
		company_email: EnvelopeSimple,
		company_address: MapPin,
		opening_hours: Clock,
		facebook_url: FacebookLogo,
		linkedin_url: LinkedinLogo,
		x_url: XLogo,
		youtube_url: YoutubeLogo
	};

	const CONTACT_KEYS = ['company_phone', 'company_whatsapp', 'company_email', 'company_address', 'opening_hours'];
	const SOCIAL_KEYS = ['facebook_url', 'linkedin_url', 'x_url', 'youtube_url'];

	const TABS = [
		{ id: 'contact', label: 'Coordonnées' },
		{ id: 'social', label: 'Réseaux sociaux' },
		{ id: 'identity', label: 'Identité' },
		{ id: 'vision', label: 'Vision & missions' },
		{ id: 'values', label: 'Valeurs & différenciateurs' }
	];
	let activeTab = $state(page.url.searchParams.get('tab') ?? 'contact');

	$effect(() => {
		const query = activeTab === 'contact' ? '' : `?tab=${activeTab}`;
		goto(`/admin/settings${query}`, { replaceState: true, noScroll: true, keepFocus: true });
	});

	let values = $state({ ...data.settings.values });
	let contactSaving = $state(false);
	let contactSaved = $state(false);
	let contactError = $state('');

	async function saveContactFields(keys: string[], event: SubmitEvent) {
		event.preventDefault();
		contactSaving = true;
		contactSaved = false;
		contactError = '';
		try {
			const subset = Object.fromEntries(keys.map((key) => [key, values[key]]));
			await apiCall('/admin/settings', { method: 'PATCH', body: { values: subset } });
			contactSaved = true;
		} catch (exception) {
			contactError =
				exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			contactSaving = false;
		}
	}

	let about = $state<CompanyAbout>(structuredClone(data.about));
	let aboutSaving = $state(false);
	let aboutSaved = $state(false);
	let aboutError = $state('');

	function addMission() {
		about.missions = [...about.missions, ''];
	}
	function removeMission(index: number) {
		about.missions = about.missions.filter((_, i) => i !== index);
	}

	function addValue() {
		about.values = [...about.values, ''];
	}
	function removeValue(index: number) {
		about.values = about.values.filter((_, i) => i !== index);
	}

	function addDifferentiator() {
		about.differentiators = [...about.differentiators, { title: '', description: '' }];
	}
	function removeDifferentiator(index: number) {
		about.differentiators = about.differentiators.filter((_, i) => i !== index);
	}

	async function saveAboutFields(fields: Partial<CompanyAbout>, event: SubmitEvent) {
		event.preventDefault();
		aboutSaving = true;
		aboutSaved = false;
		aboutError = '';
		try {
			about = await apiCall<CompanyAbout>('/admin/settings/about', {
				method: 'PATCH',
				body: fields
			});
			aboutSaved = true;
		} catch (exception) {
			aboutError =
				exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			aboutSaving = false;
		}
	}

	function saveIdentity(event: SubmitEvent) {
		saveAboutFields(
			{
				founded_year: about.founded_year,
				legal_form: about.legal_form,
				headquarters: about.headquarters
			},
			event
		);
	}

	function saveVision(event: SubmitEvent) {
		saveAboutFields(
			{
				vision: about.vision,
				missions: about.missions.map((item) => item.trim()).filter(Boolean)
			},
			event
		);
	}

	function saveValuesAndDifferentiators(event: SubmitEvent) {
		saveAboutFields(
			{
				values: about.values.map((item) => item.trim()).filter(Boolean),
				differentiators: about.differentiators
					.map((item) => ({ title: item.title.trim(), description: item.description.trim() }))
					.filter((item) => item.title && item.description)
			},
			event
		);
	}
</script>

<svelte:head>
	<title>Paramètres, panel IUMC</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-ink-950">Paramètres généraux</h1>
<p class="mt-2 text-sm text-ink-800/70">
	Coordonnées, contenu institutionnel et liens affichés sur le site public. Les valeurs
	officielles restent à confirmer par IUMC (PRD section 24).
</p>

<div class="mt-6">
	<Tabs tabs={TABS} bind:active={activeTab} />
</div>

<div class="mt-6 max-w-xl">
	{#if activeTab === 'contact' || activeTab === 'social'}
		<form
			class="flex flex-col gap-4"
			onsubmit={(event) =>
				saveContactFields(activeTab === 'contact' ? CONTACT_KEYS : SOCIAL_KEYS, event)}
		>
			{#each activeTab === 'contact' ? CONTACT_KEYS : SOCIAL_KEYS as key (key)}
				<TextField id={key} label={FIELD_LABELS[key]} icon={FIELD_ICONS[key]} bind:value={values[key]} />
			{/each}

			{#if contactError}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
					{contactError}
				</p>
			{/if}
			{#if contactSaved}
				<p class="rounded-input bg-green-500/10 px-3 py-2.5 text-sm text-green-600">
					Coordonnées enregistrées.
				</p>
			{/if}

			<button
				type="submit"
				disabled={contactSaving}
				class="inline-flex items-center gap-2 self-start rounded-pill bg-green-500 px-6 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600 disabled:opacity-60"
			>
				<FloppyDisk size={16} />
				Enregistrer
			</button>
		</form>
	{:else if activeTab === 'identity'}
		<form class="flex flex-col gap-4" onsubmit={saveIdentity}>
			<TextField id="about-year" label="Année de création" icon={CalendarBlank} bind:value={about.founded_year} />
			<TextField id="about-form" label="Forme juridique" icon={Scales} bind:value={about.legal_form} />
			<TextField id="about-hq" label="Siège" icon={Buildings} bind:value={about.headquarters} />

			{#if aboutError}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
					{aboutError}
				</p>
			{/if}
			{#if aboutSaved}
				<p class="rounded-input bg-green-500/10 px-3 py-2.5 text-sm text-green-600">Identité enregistrée.</p>
			{/if}

			<button
				type="submit"
				disabled={aboutSaving}
				class="inline-flex items-center gap-2 self-start rounded-pill bg-green-500 px-6 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600 disabled:opacity-60"
			>
				<FloppyDisk size={16} />
				Enregistrer
			</button>
		</form>
	{:else if activeTab === 'vision'}
		<form class="flex flex-col gap-5" onsubmit={saveVision}>
			<RichTextEditor
				id="about-vision"
				label="Vision à l'horizon 2030"
				bind:value={about.vision}
				placeholder="Vision institutionnelle affichée sur la page « Qui sommes-nous »…"
			/>

			<div class="flex flex-col gap-2">
				<span class="text-sm font-medium text-ink-900">Missions</span>
				{#each about.missions as _mission, i (i)}
					<div class="flex gap-2">
						<input
							type="text"
							bind:value={about.missions[i]}
							class="flex-1 rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-green-500 focus:outline-none"
						/>
						<button
							type="button"
							onclick={() => removeMission(i)}
							aria-label="Retirer cette mission"
							class="rounded-input border border-ink-900/20 p-2 text-ink-800/60 hover:border-ink-900/40"
						>
							<Trash size={14} />
						</button>
					</div>
				{/each}
				<button
					type="button"
					onclick={addMission}
					class="inline-flex items-center gap-1.5 self-start text-sm font-medium text-ink-900 hover:text-green-600"
				>
					<Plus size={14} />
					Ajouter une mission
				</button>
			</div>

			{#if aboutError}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
					{aboutError}
				</p>
			{/if}
			{#if aboutSaved}
				<p class="rounded-input bg-green-500/10 px-3 py-2.5 text-sm text-green-600">
					Vision et missions enregistrées.
				</p>
			{/if}

			<button
				type="submit"
				disabled={aboutSaving}
				class="inline-flex items-center gap-2 self-start rounded-pill bg-green-500 px-6 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600 disabled:opacity-60"
			>
				<FloppyDisk size={16} />
				Enregistrer
			</button>
		</form>
	{:else}
		<form class="flex flex-col gap-5" onsubmit={saveValuesAndDifferentiators}>
			<div class="flex flex-col gap-2">
				<span class="text-sm font-medium text-ink-900">Valeurs</span>
				<div class="flex flex-wrap gap-2">
					{#each about.values as _value, i (i)}
						<div class="flex items-center gap-1 rounded-pill border border-ink-900/20 pr-1 pl-3">
							<input
								type="text"
								bind:value={about.values[i]}
								class="w-28 bg-transparent py-1.5 text-sm text-ink-950 focus:outline-none"
							/>
							<button
								type="button"
								onclick={() => removeValue(i)}
								aria-label="Retirer cette valeur"
								class="rounded-full p-1 text-ink-800/50 hover:text-ink-900"
							>
								<Trash size={12} />
							</button>
						</div>
					{/each}
				</div>
				<button
					type="button"
					onclick={addValue}
					class="inline-flex items-center gap-1.5 self-start text-sm font-medium text-ink-900 hover:text-green-600"
				>
					<Plus size={14} />
					Ajouter une valeur
				</button>
			</div>

			<div class="flex flex-col gap-3">
				<span class="text-sm font-medium text-ink-900">L'originalité du modèle IUMC</span>
				{#each about.differentiators as _item, i (i)}
					<div class="flex flex-col gap-3 rounded-input border border-ink-900/15 p-3">
						<div class="flex items-end gap-2">
							<div class="flex-1">
								<TextField
									id={`diff-title-${i}`}
									label="Titre"
									icon={Star}
									bind:value={about.differentiators[i].title}
								/>
							</div>
							<button
								type="button"
								onclick={() => removeDifferentiator(i)}
								aria-label="Retirer cet élément"
								class="rounded-input border border-ink-900/20 p-2 text-ink-800/60 hover:border-ink-900/40"
							>
								<Trash size={14} />
							</button>
						</div>
						<RichTextEditor
							id={`diff-description-${i}`}
							label="Description"
							bind:value={about.differentiators[i].description}
							placeholder="Description de cet atout distinctif…"
						/>
					</div>
				{/each}
				<button
					type="button"
					onclick={addDifferentiator}
					class="inline-flex items-center gap-1.5 self-start text-sm font-medium text-ink-900 hover:text-green-600"
				>
					<Plus size={14} />
					Ajouter un élément
				</button>
			</div>

			{#if aboutError}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
					{aboutError}
				</p>
			{/if}
			{#if aboutSaved}
				<p class="rounded-input bg-green-500/10 px-3 py-2.5 text-sm text-green-600">
					Valeurs et différenciateurs enregistrés.
				</p>
			{/if}

			<button
				type="submit"
				disabled={aboutSaving}
				class="inline-flex items-center gap-2 self-start rounded-pill bg-green-500 px-6 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600 disabled:opacity-60"
			>
				<FloppyDisk size={16} />
				Enregistrer
			</button>
		</form>
	{/if}
</div>
