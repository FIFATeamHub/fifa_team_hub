import {useAuthStore} from "../stores/auth.js"

export function usePermissions(){

    const authStore = useAuthStore()

    const can = (action , dataTeamId = null) => {

        const user = authStore.user
        if (!user) return false

        const permissions = {
            'view:logs':           ["AUDITOR"],
            'register:players':    ["AUDITOR"],
            'view:tactics':        ["ATHELETE", "TECHNICAL_STAFF"],
            'edit:tactics':        ["TECHNICAL_STAFF"],
            'upload:med_docs':     ["MEDICAL_STAFF"],
            'upload:documents':    ["TECHNICAL_STAFF", "ATHELETE"],
            'view:med_docs':       ["TECHNICAL_STAFF", "MEDICAL_STAFF", "ORGANIZER"],
            'view:bureaucratic':   ['AUDITOR', "ATHELETE", "ORGANIZER"]
        }

        const allowedRoles = permissions[action]

        const hasRolePermission = allowedRoles?.includes(user.role) ?? false

        if (!hasRolePermission) return false

        if (user.role == "ORGANIZER"){
            return true
        }

        if (dataTeamId){
            return user.selection_id == dataTeamId 
        }

        return true

    }

    return {can}

}