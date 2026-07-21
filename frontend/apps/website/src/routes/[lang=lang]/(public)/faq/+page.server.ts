import { serverApiGet } from '@iumc/api/server';
import type { PublicFaq } from '$lib/content';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const faqs = await serverApiGet<PublicFaq[]>('/faqs', fetch);
	return { faqs };
};
