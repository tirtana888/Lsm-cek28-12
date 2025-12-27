<?php

namespace App\Services;

class LicenseService
{
    /**
     * BYPASSED - Always return true/valid
     */
    public static function verify($code = null)
    {
        return ['status' => true, 'message' => 'License verified'];
    }

    public function isValid()
    {
        return true;
    }

    public function checkLicense()
    {
        return true;
    }

    public function validatePurchaseCode($code)
    {
        return ['status' => true, 'valid' => true, 'license_type' => 'extended'];
    }

    public static function isLicenseValid()
    {
        return true;
    }
}