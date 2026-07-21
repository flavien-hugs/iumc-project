import { serverApiGet } from '@iumc/api/server';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const locations = await serverApiGet<{ city: string }[]>('/locations', fetch);
	return { cities: locations.map((location) => location.city) };
};
