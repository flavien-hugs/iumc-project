import { serverApiGet } from '@iumc/api/server';
import type { PageServerLoad } from './$types';

export interface Differentiator {
	title: string;
	description: string;
}

export interface CompanyAbout {
	founded_year: string;
	legal_form: string;
	headquarters: string;
	vision: string;
	missions: string[];
	values: string[];
	differentiators: Differentiator[];
}

export interface PublicCompany {
	about: CompanyAbout;
	contact: Record<string, string>;
}

export const load: PageServerLoad = async ({ fetch }) => {
	const [company, locations] = await Promise.all([
		serverApiGet<PublicCompany>('/company', fetch),
		serverApiGet<{ status: string }[]>('/locations', fetch)
	]);
	return { company, locationsCount: locations.length };
};
