/*
 * Copyright (c) 2009 Bea Lam. All rights reserved.
 *
 * This file is part of LightBlue.
 *
 * LightBlue is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * LightBlue is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LightBlue.  If not, see <http://www.gnu.org/licenses/>.
*/

//
//  BBLocalDevice.m
//  LightAquaBlue
//

#import <IOBluetooth/Bluetooth.h>
#import <IOBluetooth/IOBluetoothUserLib.h>
#import <IOBluetooth/IOBluetoothUtilities.h>

#import "BBLocalDevice.h"


@implementation BBLocalDevice

+ (NSString *)getName
{
	BluetoothDeviceName name;
    IOReturn result;
	
	result = IOBluetoothLocalDeviceReadName(name, NULL, NULL, NULL);
    if (result == kIOReturnSuccess) {
		NSString *s = [NSString stringWithCString:(char *)name];
		if (s != nil) 
			return s;
    }        
	
    return nil;
}

+ (NSString *)getAddressString
{
	BluetoothDeviceAddress address;
    IOReturn result;
	
	result = IOBluetoothLocalDeviceReadAddress(&address, NULL, NULL, NULL);
    if (result == kIOReturnSuccess) {
		return IOBluetoothNSStringFromDeviceAddress(&address);
    }        
	
    return nil;
}

+ (BluetoothClassOfDevice)getClassOfDevice
{
	BluetoothClassOfDevice classOfDevice;
    IOReturn result;
	
	result = IOBluetoothLocalDeviceReadClassOfDevice(&classOfDevice, NULL, NULL, NULL);
    if (result == kIOReturnSuccess) {
		return classOfDevice;
    }        
	
    return -1;
}

+ (BOOL)isPoweredOn
{
	if (!IOBluetoothLocalDeviceAvailable()) 
		return NO;
	
	BluetoothHCIPowerState powerState;
	IOReturn status = IOBluetoothLocalDeviceGetPowerState(&powerState);
	if (status != kIOReturnSuccess || powerState != kBluetoothHCIPowerStateON) 
		return NO;
	
	return YES;
}

@end
