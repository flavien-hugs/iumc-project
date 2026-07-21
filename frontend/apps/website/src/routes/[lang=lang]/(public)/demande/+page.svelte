<script lang="ts">
	import {
		Buildings,
		Calendar,
		ClipboardText,
		EnvelopeSimple,
		MapPin,
		Paperclip,
		Phone,
		Stack,
		Tag,
		User,
		UsersThree,
		WhatsappLogo,
		NotePencil
	} from 'phosphor-svelte';
	import { page } from '$app/state';
	import { apiCall, API_BASE, ApiError } from '@iumc/api';
	import type { PublicDivision } from '$lib/content';
	import Seo from '$lib/components/Seo.svelte';
	import SenufoFrieze from '$lib/illustrations/SenufoFrieze.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import TextareaField from '@iumc/ui/formulaire/TextareaField.svelte';
	import SearchSelect from '@iumc/ui/formulaire/SearchSelect.svelte';
	import FileField from '@iumc/ui/formulaire/FileField.svelte';

	const divisions = $derived((page.data.divisions ?? []) as PublicDivision[]);
	const activeDivisions = $derived(divisions.filter((division) => division.status === 'active'));
	const clientTypes = [
		{ value: 'individual', label: 'Particulier' },
		{ value: 'company', label: 'Entreprise' },
		{ value: 'industrial', label: 'Industriel ou investisseur' },
		{ value: 'developer', label: 'Promoteur immobilier' },
		{ value: 'community', label: 'Communauté villageoise' }
	];

	let fullName = $state('');
	let company = $state('');
	let phone = $state('');
	let email = $state('');
	let city = $state('');
	let clientType = $state('');
	let divisionSlug = $state(page.url.searchParams.get('division') ?? '');
	let serviceSlug = $state(page.url.searchParams.get('service') ?? '');
	let subject = $state('');
	let description = $state('');
	let contactPreference = $state('phone');
	let appointmentDate = $state('');
	let consent = $state(false);
	let honeypot = $state('');
	let attachmentFiles = $state<FileList | null>(null);

	const divisionOptions = $derived(
		activeDivisions.map((division) => ({ value: division.slug, label: division.name }))
	);
	const serviceOptions = $derived(
		(divisions.find((division) => division.slug === divisionSlug)?.services ?? []).map((service) => ({
			value: service.slug,
			label: service.title
		}))
	);

	let formState = $state<'idle' | 'sending' | 'success'>('idle');
	let reference = $state('');
	let error = $state('');

	async function submitForm(event: SubmitEvent) {
		event.preventDefault();
		if (honeypot) return;
		formState = 'sending';
		error = '';
		try {
			let attachment: string | null = null;
			const file = attachmentFiles?.[0];
			if (file) {
				const form = new FormData();
				form.append('file', file);
				const uploadResponse = await fetch(`${API_BASE}/service-requests/attachments`, {
					method: 'POST',
					body: form
				});
				if (!uploadResponse.ok) {
					const detail = await uploadResponse.json().catch(() => ({}));
					throw new ApiError(
						uploadResponse.status,
						detail.detail ?? 'Téléversement de la pièce jointe impossible.'
					);
				}
				attachment = (await uploadResponse.json()).attachment;
			}

			const result = await apiCall<{ reference: string }>('/service-requests', {
				method: 'POST',
				body: {
					full_name: fullName,
					company: company || null,
					phone,
					email: email || null,
					city: city || null,
					client_type: clientType || null,
					division: divisionSlug,
					service: serviceSlug,
					subject: subject || null,
					description,
					contact_preference: contactPreference,
					preferred_appointment_date: appointmentDate || null,
					attachment
				}
			});
			reference = result.reference;
			formState = 'success';
		} catch (exception) {
			formState = 'idle';
			error =
				exception instanceof ApiError
					? exception.message
					: "L'envoi a échoué. Vérifiez votre connexion et réessayez.";
		}
	}
</script>

<Seo
	title="Demander un accompagnement, IUMC"
	description="Décrivez votre besoin à IUMC : un conseiller vous recontacte pour votre demande d'accompagnement juridique, foncier, immobilier ou industriel."
/>

<section class="mx-auto max-w-2xl px-6 py-16 lg:px-10">
	<h1 class="text-4xl font-semibold text-ink-950 md:text-5xl">Demander un accompagnement</h1>
	<p class="mt-4 max-w-[55ch] text-ink-800/80">
		Décrivez votre besoin, un membre de l'équipe IUMC vous recontacte pour la suite.
	</p>

	<SenufoFrieze class="mt-8 h-5 w-full text-gold-500/30" />

	{#if formState === 'success'}
		<div class="mt-10 rounded-card bg-paper-100 p-8">
			<h2 class="text-xl font-semibold text-ink-950">Demande envoyée</h2>
			<p class="mt-2 text-sm text-ink-800/70">
				Merci, votre demande a bien été transmise à IUMC sous la référence
				<span class="font-bold text-green-600">{reference}</span>. Conservez-la pour vos
				échanges : un conseiller vous recontacte selon votre préférence de contact.
			</p>
		</div>
	{:else}
		<form class="mt-10 flex flex-col gap-5" onsubmit={submitForm}>
			<div class="hidden" aria-hidden="true">
				<label for="site-web">Ne pas remplir</label>
				<input id="site-web" type="text" tabindex="-1" autocomplete="off" bind:value={honeypot} />
			</div>

			{#if error}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
					{error}
				</p>
			{/if}

			<div class="grid gap-5 sm:grid-cols-2">
				<TextField id="nom" label="Nom et prénoms" icon={User} required bind:value={fullName} />
				<TextField
					id="entreprise"
					label="Entreprise (si applicable)"
					icon={Buildings}
					bind:value={company}
				/>
			</div>

			<div class="grid gap-5 sm:grid-cols-2">
				<TextField
					id="telephone"
					label="Téléphone"
					type="tel"
					icon={Phone}
					required
					bind:value={phone}
				/>
				<TextField id="email" label="E-mail" type="email" icon={EnvelopeSimple} bind:value={email} />
			</div>

			<div class="grid gap-5 sm:grid-cols-2">
				<TextField id="ville" label="Ville" icon={MapPin} list="villes" bind:value={city} />
				<datalist id="villes">
					{#each page.data.cities as cityOption (cityOption)}
						<option value={cityOption}></option>
					{/each}
				</datalist>

				<SearchSelect
					id="type-client"
					label="Type de client"
					icon={UsersThree}
					options={clientTypes}
					bind:value={clientType}
				/>
			</div>

			<div class="grid gap-5 sm:grid-cols-2">
				<SearchSelect
					id="pole"
					label="Pôle"
					icon={Stack}
					options={divisionOptions}
					required
					bind:value={divisionSlug}
					onchange={() => (serviceSlug = '')}
				/>
				<SearchSelect
					id="service"
					label="Service"
					icon={ClipboardText}
					options={serviceOptions}
					required
					disabled={!divisionSlug}
					bind:value={serviceSlug}
				/>
			</div>

			<TextField id="objet" label="Objet de la demande" icon={Tag} required bind:value={subject} />

			<TextareaField
				id="description"
				label="Description du besoin"
				icon={NotePencil}
				required
				bind:value={description}
			/>

			<fieldset class="flex flex-col gap-2">
				<legend class="text-sm font-medium text-ink-900">Préférence de contact</legend>
				<div class="flex flex-wrap gap-5">
					{#each [{ value: 'phone', label: 'Téléphone', icon: Phone }, { value: 'email', label: 'E-mail', icon: EnvelopeSimple }, { value: 'whatsapp', label: 'WhatsApp', icon: WhatsappLogo }] as option (option.value)}
						<label class="flex items-center gap-2 text-sm text-ink-800">
							<input
								type="radio"
								name="preference-contact"
								value={option.value}
								bind:group={contactPreference}
								class="accent-green-500"
							/>
							<option.icon size={16} class="text-ink-800/50" />
							{option.label}
						</label>
					{/each}
				</div>
			</fieldset>

			<div class="grid gap-5 sm:grid-cols-2">
				<TextField
					id="date-rdv"
					label="Date souhaitée de rendez-vous (facultatif)"
					type="date"
					icon={Calendar}
					bind:value={appointmentDate}
				/>
				<FileField
					id="piece-jointe"
					label="Pièce jointe (facultatif)"
					icon={Paperclip}
					accept=".pdf,.jpg,.jpeg,.png"
					maxSizeMb={10}
					bind:files={attachmentFiles}
				/>
			</div>

			<label class="flex items-start gap-2.5 text-xs text-ink-800/70">
				<input type="checkbox" required bind:checked={consent} class="mt-0.5 accent-green-500" />
				J'accepte que mes informations soient utilisées par IUMC pour traiter ma demande,
				conformément à la politique de confidentialité.
			</label>

			<button
				type="submit"
				disabled={formState === 'sending'}
				class="rounded-pill bg-green-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-green-600 active:scale-[0.98] disabled:opacity-60"
			>
				{formState === 'sending' ? 'Envoi en cours…' : 'Envoyer ma demande'}
			</button>
		</form>
	{/if}
</section>
