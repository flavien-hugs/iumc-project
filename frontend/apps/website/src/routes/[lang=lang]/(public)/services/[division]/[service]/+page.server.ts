import { error } from '@sveltejs/kit';
import { serverApiGet } from '@iumc/api/server';
import type { PublicFaq } from '$lib/content';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, parent, fetch }) => {
	const { divisions } = await parent();
	const division = divisions.find((item) => item.slug === params.division);
	const service = division?.services.find((item) => item.slug === params.service);
	if (!division || !service) {
		error(404, 'Service introuvable');
	}
	const faqs = await serverApiGet<PublicFaq[]>('/faqs', fetch);
	// FAQ liées au service ou au pôle, sinon les 3 premières générales.
	const related = faqs.filter(
		(faq) => faq.service_id === service.id || (faq.division_id === division.id && !faq.service_id)
	);
	const general = faqs.filter((faq) => !faq.division_id && !faq.service_id);
	return { division, service, faqs: (related.length > 0 ? related : general).slice(0, 4) };
};
