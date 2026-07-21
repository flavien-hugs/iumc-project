<script lang="ts">
	import { FacebookLogo, LinkedinLogo, WhatsappLogo, XLogo, YoutubeLogo } from 'phosphor-svelte';
	import { page } from '$app/state';
	import type { PublicDivision } from '$lib/content';

	const divisions = $derived((page.data.divisions ?? []) as PublicDivision[]);

	const navigation = [
		{ href: '/fr/qui-sommes-nous', label: 'Qui sommes-nous' },
		{ href: '/fr/services', label: 'Nos pôles' },
		{ href: '/fr/implantations', label: 'Implantations' },
		{ href: '/fr/actualites', label: 'Actualités' },
		{ href: '/fr/contact', label: 'Contact' },
		{ href: '/fr/demande', label: "Demande d'accompagnement" }
	];

	const socials = [
		{ label: 'Facebook', href: '#', icon: FacebookLogo },
		{ label: 'LinkedIn', href: '#', icon: LinkedinLogo },
		{ label: 'WhatsApp', href: '#', icon: WhatsappLogo },
		{ label: 'X', href: '#', icon: XLogo },
		{ label: 'YouTube', href: '#', icon: YoutubeLogo }
	];
</script>

<footer class="bg-ink-950 text-paper-100">
	<div
		class="mx-auto grid max-w-7xl gap-x-8 gap-y-12 px-6 py-16 sm:grid-cols-2 lg:grid-cols-6 lg:px-10"
	>
		<div class="sm:col-span-2">
			<img
				src="/logo-iumc.png"
				alt="IUMC — Ivoire Univers Multiservices et Commerce"
				class="h-28 w-auto"
			/>
			<p class="mt-4 max-w-[32ch] text-sm text-paper-100/70">
				Ivoire Univers Multiservices et Commerces. Accompagnement juridique, foncier,
				immobilier et industriel en Côte d'Ivoire.
			</p>
			<div class="mt-6 flex gap-3">
				{#each socials as social (social.label)}
					<a
						href={social.href}
						aria-label={social.label}
						class="flex h-9 w-9 items-center justify-center rounded-full border border-paper-100/15 text-paper-100/80 transition-colors hover:border-green-500 hover:text-green-500"
					>
						<social.icon size={18} />
					</a>
				{/each}
			</div>
		</div>

		<div>
			<p class="text-xs font-medium tracking-wide text-paper-100/50 uppercase">Navigation</p>
			<ul class="mt-3 space-y-2 text-sm">
				{#each navigation as link (link.href)}
					<li>
						<a href={link.href} class="text-paper-100/80 transition-colors hover:text-green-500">
							{link.label}
						</a>
					</li>
				{/each}
			</ul>
		</div>

		<div>
			<p class="text-xs font-medium tracking-wide text-paper-100/50 uppercase">Nos pôles</p>
			<ul class="mt-3 space-y-2 text-sm">
				{#each divisions as division (division.slug)}
					<li>
						<a
							href={`/fr/services/${division.slug}`}
							class="text-paper-100/80 transition-colors hover:text-green-500"
						>
							{division.name}
						</a>
					</li>
				{/each}
			</ul>
		</div>

		<div>
			<p class="text-xs font-medium tracking-wide text-paper-100/50 uppercase">Adresse</p>
			<p class="mt-3 text-sm text-paper-100/80">
				Bouaké, quartier Koko<br />
				(entre la maternité et la mairie)
			</p>
		</div>

		<div>
			<p class="text-xs font-medium tracking-wide text-paper-100/50 uppercase">Contact</p>
			<ul class="mt-3 space-y-1.5 text-sm text-paper-100/80">
				<li>contact@iumc.ci</li>
				<li>+225 XX XX XX XX XX</li>
			</ul>
		</div>
	</div>

	<div
		class="mx-auto flex max-w-7xl flex-col gap-3 border-t border-paper-100/10 px-6 py-6 text-xs text-paper-100/50 sm:flex-row sm:items-center sm:justify-between lg:px-10"
	>
		<p>© {new Date().getFullYear()} IUMC. Tous droits réservés.</p>
		<div class="flex gap-5">
			<a href="/fr/faq" class="hover:text-paper-100">FAQ</a>
			<a href="/fr/mentions-legales" class="hover:text-paper-100">Mentions légales</a>
			<a href="/fr/confidentialite" class="hover:text-paper-100">Confidentialité</a>
		</div>
	</div>
</footer>
