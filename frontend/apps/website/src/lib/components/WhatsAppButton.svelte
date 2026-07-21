<script lang="ts">
	import { WhatsappLogo } from 'phosphor-svelte';

	const message = encodeURIComponent(
		"Bonjour IUMC, je souhaite obtenir des informations concernant vos services."
	);
	const phoneNumber = '225XXXXXXXXXX';
</script>

<a
	href={`https://wa.me/${phoneNumber}?text=${message}`}
	target="_blank"
	rel="noopener noreferrer"
	aria-label="Échanger avec IUMC sur WhatsApp"
	class="fixed right-6 bottom-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-green-500 text-ink-950 shadow-lg shadow-ink-950/20 transition-transform hover:bg-green-600 active:scale-[0.98]"
>
	<WhatsappLogo size={26} weight="fill" />
</a>
