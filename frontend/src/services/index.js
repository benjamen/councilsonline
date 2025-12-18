/**
 * Lodgeick Service Layer
 * Central export point for all API services
 *
 * Usage:
 *   import { requestService, councilService } from '@/services'
 *
 *   // Or import individually:
 *   import { requestService } from '@/services/api/request.service'
 */

// Export API client
export { apiClient, BaseAPIClient } from "./api/base"

// Export individual services
export { requestService, RequestService } from "./api/request.service"
export { councilService, CouncilService } from "./api/council.service"
export { userService, UserService } from "./api/user.service"
export {
	applicationService,
	ApplicationService,
} from "./api/application.service"
export {
	requestTypeService,
	RequestTypeService,
} from "./api/requestType.service"
export { rfqService, RFQService } from "./api/rfq.service"
export { documentService, DocumentService } from "./api/document.service"

import { applicationService } from "./api/application.service"
// Convenience: export all services as a single object
// Import them locally to avoid referencing them before they're imported
import { apiClient } from "./api/base"
import { councilService } from "./api/council.service"
import { documentService } from "./api/document.service"
import { requestService } from "./api/request.service"
import { requestTypeService } from "./api/requestType.service"
import { rfqService } from "./api/rfq.service"
import { userService } from "./api/user.service"

export default {
	apiClient,
	requestService,
	councilService,
	userService,
	applicationService,
	requestTypeService,
	rfqService,
	documentService,
}
