import { serverApiGet } from '@iumc/api/server';
import type { PageServerLoad } from './$types';

export interface PublicLocation {
	name: string;
	city: string;
	district: string | null;
	address: string | null;
	latitude: number | null;
	longitude: number | null;
	status: string;
	phone: string | null;
	whatsapp: string | null;
	opening_hours: string | null;
}

export const load: PageServerLoad = async ({ fetch }) => {
	const locations = await serverApiGet<PublicLocation[]>('/locations', fetch);
	return { locations };
};
