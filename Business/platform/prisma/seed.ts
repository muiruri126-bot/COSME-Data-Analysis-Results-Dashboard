import { PrismaClient, ListingType } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // ─── Service Categories ───

  const categories = await Promise.all([
    // A. Home & Domestic Services
    prisma.serviceCategory.upsert({
      where: { slug: 'house-help' },
      update: {},
      create: {
        name: 'House Help',
        slug: 'house-help',
        description: 'General domestic workers for households',
        listingType: ListingType.job,
        sortOrder: 1,
        attributeSchema: {
          live_in: { type: 'boolean', label: 'Live-in' },
          duties: {
            type: 'multi-select',
            label: 'Duties',
            options: ['Cooking', 'Cleaning', 'Laundry', 'Ironing', 'Shopping', 'Childcare', 'Elderly care'],
          },
          experience_years: { type: 'number', label: 'Minimum years of experience' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'nanny' },
      update: {},
      create: {
        name: 'Nanny / Babysitter',
        slug: 'nanny',
        description: 'Childcare providers for families',
        listingType: ListingType.job,
        sortOrder: 2,
        attributeSchema: {
          age_group: {
            type: 'multi-select',
            label: 'Child age group',
            options: ['Infant (0-1)', 'Toddler (1-3)', 'Pre-school (3-5)', 'School-age (5-12)', 'Teenager (12+)'],
          },
          live_in: { type: 'boolean', label: 'Live-in' },
          certifications: { type: 'text', label: 'Relevant certifications' },
          number_of_children: { type: 'number', label: 'Number of children' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'caregiver' },
      update: {},
      create: {
        name: 'Caregiver',
        slug: 'caregiver',
        description: 'Care for elderly or persons with disabilities',
        listingType: ListingType.job,
        sortOrder: 3,
        attributeSchema: {
          care_type: {
            type: 'multi-select',
            label: 'Type of care',
            options: ['Elderly care', 'Disability care', 'Post-surgery care', 'Palliative care'],
          },
          live_in: { type: 'boolean', label: 'Live-in' },
          medical_training: { type: 'boolean', label: 'Has medical/nursing training' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'cleaner' },
      update: {},
      create: {
        name: 'Cleaner',
        slug: 'cleaner',
        description: 'Home and office cleaning services',
        listingType: ListingType.job,
        sortOrder: 4,
        attributeSchema: {
          cleaning_type: {
            type: 'multi-select',
            label: 'Type of cleaning',
            options: ['Residential', 'Office/Commercial', 'Deep cleaning', 'Move-in/Move-out', 'Post-construction'],
          },
          frequency: {
            type: 'select',
            label: 'Frequency',
            options: ['One-time', 'Daily', 'Weekly', 'Bi-weekly', 'Monthly'],
          },
          supplies_provided: { type: 'boolean', label: 'Cleaning supplies provided' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'gardener' },
      update: {},
      create: {
        name: 'Gardener / Groundsman',
        slug: 'gardener',
        description: 'Garden maintenance and landscaping',
        listingType: ListingType.job,
        sortOrder: 5,
        attributeSchema: {
          services: {
            type: 'multi-select',
            label: 'Services needed',
            options: ['Lawn mowing', 'Landscaping', 'Tree trimming', 'Planting', 'Watering', 'General maintenance'],
          },
          property_size: {
            type: 'select',
            label: 'Property size',
            options: ['Small (< 1/4 acre)', 'Medium (1/4 - 1 acre)', 'Large (> 1 acre)'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'plumber' },
      update: {},
      create: {
        name: 'Plumber',
        slug: 'plumber',
        description: 'Plumbing installation and repair',
        listingType: ListingType.service_request,
        sortOrder: 6,
        attributeSchema: {
          job_type: {
            type: 'multi-select',
            label: 'Type of work',
            options: ['Leak repair', 'Pipe installation', 'Drain unclogging', 'Water heater', 'Toilet repair', 'Tap/faucet', 'Sewer line'],
          },
          urgency: {
            type: 'select',
            label: 'Urgency',
            options: ['Emergency (today)', 'Urgent (1-2 days)', 'Scheduled (this week)', 'Flexible'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'electrician' },
      update: {},
      create: {
        name: 'Electrician',
        slug: 'electrician',
        description: 'Electrical installation and repair',
        listingType: ListingType.service_request,
        sortOrder: 7,
        attributeSchema: {
          job_type: {
            type: 'multi-select',
            label: 'Type of work',
            options: ['Wiring', 'Socket/switch installation', 'Lighting', 'Circuit breaker', 'Generator', 'Solar installation', 'Fault diagnosis'],
          },
          urgency: {
            type: 'select',
            label: 'Urgency',
            options: ['Emergency (today)', 'Urgent (1-2 days)', 'Scheduled (this week)', 'Flexible'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'carpenter' },
      update: {},
      create: {
        name: 'Carpenter',
        slug: 'carpenter',
        description: 'Woodwork, furniture, and carpentry services',
        listingType: ListingType.service_request,
        sortOrder: 8,
        attributeSchema: {
          job_type: {
            type: 'multi-select',
            label: 'Type of work',
            options: ['Furniture making', 'Furniture repair', 'Door/window fitting', 'Roofing', 'Shelving', 'Kitchen cabinets', 'General woodwork'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'painter' },
      update: {},
      create: {
        name: 'Painter',
        slug: 'painter',
        description: 'Interior and exterior painting',
        listingType: ListingType.service_request,
        sortOrder: 9,
        attributeSchema: {
          paint_type: {
            type: 'select',
            label: 'Type',
            options: ['Interior', 'Exterior', 'Both'],
          },
          rooms: { type: 'number', label: 'Number of rooms' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'mason' },
      update: {},
      create: {
        name: 'Mason',
        slug: 'mason',
        description: 'Masonry, tiling, and construction work',
        listingType: ListingType.service_request,
        sortOrder: 10,
        attributeSchema: {
          job_type: {
            type: 'multi-select',
            label: 'Type of work',
            options: ['Tiling', 'Plastering', 'Block/brick laying', 'Foundation', 'Renovation', 'Paving'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'driver' },
      update: {},
      create: {
        name: 'Driver / Chauffeur',
        slug: 'driver',
        description: 'Personal or company driving services',
        listingType: ListingType.job,
        sortOrder: 11,
        attributeSchema: {
          license_class: {
            type: 'select',
            label: 'License class required',
            options: ['Class B (Light vehicle)', 'Class C (Medium vehicle)', 'Class D (Heavy vehicle)', 'Any'],
          },
          vehicle_provided: { type: 'boolean', label: 'Vehicle provided by employer' },
          driving_type: {
            type: 'select',
            label: 'Type',
            options: ['Personal', 'Corporate', 'Delivery', 'Tour/Safari'],
          },
        },
      },
    }),

    // B. Housing & Space
    prisma.serviceCategory.upsert({
      where: { slug: 'rental-apartment' },
      update: {},
      create: {
        name: 'Rental - Apartment / House',
        slug: 'rental-apartment',
        description: 'Apartments, houses, and flats for rent',
        listingType: ListingType.rental,
        sortOrder: 20,
        attributeSchema: {
          property_type: {
            type: 'select',
            label: 'Property type',
            options: ['Bedsitter', 'Studio', '1 Bedroom', '2 Bedroom', '3 Bedroom', '4+ Bedroom', 'Mansion', 'Townhouse', 'Maisonette'],
          },
          furnished: {
            type: 'select',
            label: 'Furnishing',
            options: ['Unfurnished', 'Semi-furnished', 'Fully furnished'],
          },
          amenities: {
            type: 'multi-select',
            label: 'Amenities',
            options: ['Water 24/7', 'Backup water', 'Parking', 'Security', 'CCTV', 'Gym', 'Pool', 'Elevator', 'Balcony', 'Garden', 'WiFi-ready', 'Generator backup', 'Borehole'],
          },
          deposit_months: { type: 'number', label: 'Deposit (months)' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'short-term-rental' },
      update: {},
      create: {
        name: 'Short-term Rental / BnB',
        slug: 'short-term-rental',
        description: 'Bedsitters, guest rooms, hostels, BnB-style units',
        listingType: ListingType.rental,
        sortOrder: 21,
        attributeSchema: {
          room_type: {
            type: 'select',
            label: 'Room type',
            options: ['Private room', 'Shared room', 'Entire place', 'Hostel bed'],
          },
          amenities: {
            type: 'multi-select',
            label: 'Amenities',
            options: ['WiFi', 'Kitchen', 'Hot water', 'TV', 'Parking', 'Laundry', 'Security'],
          },
          min_nights: { type: 'number', label: 'Minimum nights' },
          max_guests: { type: 'number', label: 'Maximum guests' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'shared-housing' },
      update: {},
      create: {
        name: 'Shared Housing / Roommate',
        slug: 'shared-housing',
        description: 'Find roommates or shared living spaces',
        listingType: ListingType.rental,
        sortOrder: 22,
        attributeSchema: {
          total_rooms: { type: 'number', label: 'Total rooms in house' },
          available_rooms: { type: 'number', label: 'Rooms available' },
          preferred_gender: {
            type: 'select',
            label: 'Preferred gender',
            options: ['Male', 'Female', 'Any'],
          },
          house_rules: {
            type: 'multi-select',
            label: 'House rules',
            options: ['No smoking', 'No pets', 'No parties', 'Quiet hours', 'No overnight guests'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'office-space' },
      update: {},
      create: {
        name: 'Office / Co-working Space',
        slug: 'office-space',
        description: 'Office spaces and co-working desks',
        listingType: ListingType.space,
        sortOrder: 23,
        attributeSchema: {
          space_type: {
            type: 'select',
            label: 'Space type',
            options: ['Dedicated desk', 'Hot desk', 'Private office', 'Meeting room', 'Virtual office'],
          },
          capacity: { type: 'number', label: 'Capacity (persons)' },
          amenities: {
            type: 'multi-select',
            label: 'Amenities',
            options: ['WiFi', 'Printer', 'Meeting rooms', 'Kitchen', 'Parking', 'Reception', '24/7 access', 'Backup power'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'event-venue' },
      update: {},
      create: {
        name: 'Event Venue',
        slug: 'event-venue',
        description: 'Venues for events, conferences, and gatherings',
        listingType: ListingType.space,
        sortOrder: 24,
        attributeSchema: {
          venue_type: {
            type: 'select',
            label: 'Venue type',
            options: ['Hall', 'Garden/Grounds', 'Conference room', 'Tent/Marquee', 'Restaurant/Hotel', 'Rooftop'],
          },
          capacity: { type: 'number', label: 'Maximum capacity' },
          amenities: {
            type: 'multi-select',
            label: 'Features',
            options: ['Catering available', 'Sound system', 'Projector', 'Parking', 'Tables & chairs', 'AC', 'Stage', 'Kitchen'],
          },
        },
      },
    }),

    // C. Professional & Skill-based Services
    prisma.serviceCategory.upsert({
      where: { slug: 'tutor' },
      update: {},
      create: {
        name: 'Tutor',
        slug: 'tutor',
        description: 'Home and online tutoring services',
        listingType: ListingType.service_request,
        sortOrder: 30,
        attributeSchema: {
          subjects: {
            type: 'multi-select',
            label: 'Subjects',
            options: ['Mathematics', 'English', 'Kiswahili', 'Sciences', 'Business Studies', 'Computer Studies', 'Music', 'Languages', 'Other'],
          },
          level: {
            type: 'select',
            label: 'Student level',
            options: ['Primary', 'Secondary (Form 1-2)', 'Secondary (Form 3-4)', 'College/University', 'Adult learner'],
          },
          mode: {
            type: 'select',
            label: 'Mode',
            options: ['In-person (home)', 'In-person (tutor location)', 'Online', 'Hybrid'],
          },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'freelancer' },
      update: {},
      create: {
        name: 'Freelancer',
        slug: 'freelancer',
        description: 'Graphic designers, photographers, writers, digital marketers',
        listingType: ListingType.service_request,
        sortOrder: 31,
        attributeSchema: {
          specialization: {
            type: 'multi-select',
            label: 'Specialization',
            options: ['Graphic design', 'Photography', 'Videography', 'Writing/Content', 'Social media management', 'Digital marketing', 'Web development', 'Translation'],
          },
          delivery: {
            type: 'select',
            label: 'Delivery',
            options: ['Remote', 'On-site', 'Hybrid'],
          },
          portfolio_url: { type: 'text', label: 'Portfolio URL' },
        },
      },
    }),

    prisma.serviceCategory.upsert({
      where: { slug: 'tech-support' },
      update: {},
      create: {
        name: 'Tech Support',
        slug: 'tech-support',
        description: 'Phone repair, computer repair, IT support',
        listingType: ListingType.service_request,
        sortOrder: 32,
        attributeSchema: {
          device_type: {
            type: 'multi-select',
            label: 'Device type',
            options: ['Phone', 'Laptop', 'Desktop', 'Printer', 'Network/Router', 'CCTV/Security', 'Other'],
          },
          service_type: {
            type: 'multi-select',
            label: 'Service needed',
            options: ['Hardware repair', 'Software troubleshooting', 'Virus removal', 'Data recovery', 'Setup/Installation', 'Networking', 'Consultation'],
          },
          urgency: {
            type: 'select',
            label: 'Urgency',
            options: ['Emergency (today)', 'Urgent (1-2 days)', 'Scheduled', 'Flexible'],
          },
        },
      },
    }),
  ]);

  console.log(`✅ Created ${categories.length} service categories`);

  // ─── Skills per category ───

  const skillsData: { categorySlug: string; skills: string[] }[] = [
    {
      categorySlug: 'house-help',
      skills: ['Cooking', 'Cleaning', 'Laundry & Ironing', 'Shopping & Errands', 'Basic childcare', 'Elderly care', 'Pet care', 'Organizing'],
    },
    {
      categorySlug: 'nanny',
      skills: ['Infant care', 'Toddler care', 'School-age childcare', 'First aid', 'Meal preparation for children', 'Homework help', 'Special needs care'],
    },
    {
      categorySlug: 'caregiver',
      skills: ['Elderly care', 'Disability care', 'Medication management', 'Physical therapy assistance', 'Meal preparation', 'Mobility assistance', 'Basic nursing'],
    },
    {
      categorySlug: 'cleaner',
      skills: ['Residential cleaning', 'Office cleaning', 'Deep cleaning', 'Carpet cleaning', 'Window cleaning', 'Post-construction cleanup'],
    },
    {
      categorySlug: 'gardener',
      skills: ['Lawn care', 'Landscaping', 'Tree trimming', 'Irrigation', 'Flower gardening', 'Kitchen garden', 'Pest control'],
    },
    {
      categorySlug: 'plumber',
      skills: ['Pipe fitting', 'Leak repair', 'Drain clearing', 'Water heater', 'Toilet installation', 'Tap repair', 'Sewer line'],
    },
    {
      categorySlug: 'electrician',
      skills: ['House wiring', 'Socket installation', 'Lighting', 'Circuit breakers', 'Generator maintenance', 'Solar installation', 'Fault finding'],
    },
    {
      categorySlug: 'carpenter',
      skills: ['Furniture making', 'Door fitting', 'Window fitting', 'Kitchen cabinets', 'Roofing', 'Ceiling work', 'General woodwork'],
    },
    {
      categorySlug: 'painter',
      skills: ['Interior painting', 'Exterior painting', 'Spray painting', 'Wallpaper installation', 'Texture painting'],
    },
    {
      categorySlug: 'mason',
      skills: ['Tiling', 'Plastering', 'Brick laying', 'Foundation work', 'Paving', 'Renovation', 'Waterproofing'],
    },
    {
      categorySlug: 'driver',
      skills: ['Manual transmission', 'Automatic transmission', 'Long-distance driving', 'City driving', 'Defensive driving', 'Vehicle maintenance basics'],
    },
    {
      categorySlug: 'tutor',
      skills: ['Mathematics', 'English', 'Kiswahili', 'Sciences', 'Business Studies', 'Computer Studies', 'Exam preparation', 'Special needs education'],
    },
    {
      categorySlug: 'freelancer',
      skills: ['Graphic design', 'Photography', 'Videography', 'Content writing', 'Social media', 'Web development', 'SEO', 'Digital marketing'],
    },
    {
      categorySlug: 'tech-support',
      skills: ['Phone repair', 'Laptop repair', 'Networking', 'Software installation', 'Data recovery', 'Virus removal', 'CCTV installation'],
    },
  ];

  let totalSkills = 0;
  for (const { categorySlug, skills } of skillsData) {
    const category = await prisma.serviceCategory.findUnique({
      where: { slug: categorySlug },
    });

    if (!category) continue;

    for (const skillName of skills) {
      const slug = skillName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
      await prisma.skill.upsert({
        where: {
          categoryId_slug: {
            categoryId: category.id,
            slug,
          },
        },
        update: {},
        create: {
          categoryId: category.id,
          name: skillName,
          slug,
        },
      });
      totalSkills++;
    }
  }

  console.log(`✅ Created ${totalSkills} skills across categories`);
  console.log('🎉 Seed complete!');
}

main()
  .catch((e) => {
    console.error('❌ Seed failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
