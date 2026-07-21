<script lang="ts">
	import { Clock, EnvelopeSimple, MapPin, NotePencil, Phone, Tag, User, WhatsappLogo } from 'phosphor-svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import TextareaField from '@iumc/ui/formulaire/TextareaField.svelte';
	import GoldWeightMotif from '$lib/illustrations/GoldWeightMotif.svelte';
	import { reveal } from '$lib/actions/reveal';
	import { apiCall, ApiError } from '@iumc/api';

	let name = $state('');
	let phone = $state('');
	let email = $state('');
	let subject = $state('');
	let message = $state('');
	let consent = $state(false);
	// Champ honeypot : invisible pour un visiteur humain, souvent rempli par les robots.
	let honeypot = $state('');

	let formState = $state<'idle' | 'sending' | 'success'>('idle');
	let error = $state('');

	async function submitForm(event: SubmitEvent) {
		event.preventDefault();
		if (honeypot) return;
		formState = 'sending';
		error = '';
		try {
			await apiCall('/contact', {
				method: 'POST',
				body: { name, phone, email: email || null, subject, message }
			});
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

<svelte:head>
	<title>Contact, IUMC</title>
	<meta
		name="description"
		content="Contactez IUMC par téléphone, e-mail, WhatsApp ou via le formulaire de contact."
	/>
</svelte:head>

<section class="relative mx-auto grid max-w-7xl gap-16 overflow-hidden px-6 py-16 md:grid-cols-2 lg:px-10">
	<GoldWeightMotif
		class="parallax-lent pointer-events-none absolute -bottom-16 -left-20 h-72 w-72 text-ink-900/4"
	/>
	<div class="relative" use:reveal>
		<h1 class="text-4xl font-semibold text-ink-950 md:text-5xl">Contact</h1>
		<p class="mt-4 max-w-[46ch] text-ink-800/80">
			Une question, un besoin d'accompagnement ? L'équipe IUMC vous répond.
		</p>

		<dl class="mt-10 space-y-6">
			<div class="flex gap-3">
				<MapPin size={20} class="mt-0.5 shrink-0 text-ink-800/50" />
				<div>
					<dt class="text-sm font-medium text-ink-950">Siège</dt>
					<dd class="text-sm text-ink-800/70">Bouaké, quartier Koko (entre la maternité et la mairie)</dd>
				</div>
			</div>
			<div class="flex gap-3">
				<Phone size={20} class="mt-0.5 shrink-0 text-ink-800/50" />
				<div>
					<dt class="text-sm font-medium text-ink-950">Téléphone</dt>
					<dd class="text-sm text-ink-800/70">
						Fixe : +225 XX XX XX XX XX<br />
						Orange : +225 XX XX XX XX XX · MTN : +225 XX XX XX XX XX · Moov : +225 XX XX
						XX XX XX
					</dd>
				</div>
			</div>
			<div class="flex gap-3">
				<EnvelopeSimple size={20} class="mt-0.5 shrink-0 text-ink-800/50" />
				<div>
					<dt class="text-sm font-medium text-ink-950">E-mail</dt>
					<dd class="text-sm text-ink-800/70">contact@iumc.ci</dd>
				</div>
			</div>
			<div class="flex gap-3">
				<Clock size={20} class="mt-0.5 shrink-0 text-ink-800/50" />
				<div>
					<dt class="text-sm font-medium text-ink-950">Horaires</dt>
					<dd class="text-sm text-ink-800/70">Du lundi au vendredi, 8h à 17h</dd>
				</div>
			</div>
		</dl>

		<a
			href="https://wa.me/225XXXXXXXXXX"
			target="_blank"
			rel="noopener noreferrer"
			class="mt-8 inline-flex items-center gap-2 rounded-pill bg-gold-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-gold-600 active:scale-[0.98]"
		>
			<WhatsappLogo size={18} weight="fill" />
			Échanger sur WhatsApp
		</a>
	</div>

	<div class="relative rounded-card bg-paper-100 p-8" use:reveal={{ delay: 120 }}>
		{#if formState === 'success'}
			<div class="flex flex-col items-start gap-3 py-8">
				<h2 class="text-xl font-semibold text-ink-950">Message envoyé</h2>
				<p class="text-sm text-ink-800/70">
					Merci, votre message a bien été transmis à IUMC. Un conseiller vous recontacte
					dans les meilleurs délais.
				</p>
			</div>
		{:else}
			<form class="flex flex-col gap-5" onsubmit={submitForm}>
				<div class="hidden" aria-hidden="true">
					<label for="site-web">Ne pas remplir</label>
					<input id="site-web" type="text" tabindex="-1" autocomplete="off" bind:value={honeypot} />
				</div>

				{#if error}
					<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
						{error}
					</p>
				{/if}

				<TextField id="nom" label="Nom et prénoms" icon={User} required bind:value={name} />

				<div class="grid gap-5 sm:grid-cols-2">
					<TextField
						id="telephone"
						label="Téléphone"
						type="tel"
						icon={Phone}
						required
						bind:value={phone}
					/>
					<TextField
						id="email"
						label="E-mail"
						type="email"
						icon={EnvelopeSimple}
						bind:value={email}
					/>
				</div>

				<TextField id="objet" label="Objet" icon={Tag} required bind:value={subject} />

				<TextareaField id="message" label="Message" icon={NotePencil} required bind:value={message} />

				<label class="flex items-start gap-2.5 text-xs text-ink-800/70">
					<input
						type="checkbox"
						required
						bind:checked={consent}
						class="mt-0.5 accent-gold-500"
					/>
					J'accepte que mes informations soient utilisées par IUMC pour traiter ma demande,
					conformément à la politique de confidentialité.
				</label>

				<button
					type="submit"
					disabled={formState === 'sending'}
					class="rounded-pill bg-gold-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-gold-600 active:scale-[0.98] disabled:opacity-60"
				>
					{formState === 'sending' ? 'Envoi en cours…' : 'Envoyer le message'}
				</button>
			</form>
		{/if}
	</div>
</section>
